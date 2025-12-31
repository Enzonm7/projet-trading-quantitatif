"""Module Backtester pour la simulation de stratégies de pairs trading."""

import pandas as pd
import numpy as np
from typing import Dict, Tuple


class Backtester:
    """
    Classe responsable de la simulation de stratégies de pairs trading
    sur données historiques et du calcul des métriques de performance.
    """
    
    def __init__(self, capital_initial: float = 10000.0, seuil_entree: float = 2.0, seuil_sortie: float = 0.5):
        """
        Initialise le Backtester.
        
        Args:
            capital_initial: Capital de départ en euros (défaut: 10000.0)
            seuil_entree: Z-score pour entrée en position (défaut: 2.0)
            seuil_sortie: Z-score pour sortie de position (défaut: 0.5)
        """
        self.capital_initial = capital_initial
        self.seuil_entree = seuil_entree
        self.seuil_sortie = seuil_sortie
    
    
    def calculer_spread(self, prix_a: pd.Series, prix_b: pd.Series, ratio: float) -> pd.Series:
        """
        Calcule le spread entre deux séries de prix.
        
        Le spread représente la différence entre le prix de l'action A
        et le prix ajusté de l'action B selon le ratio de couverture.
        
        Args:
            prix_a: Série de prix de l'action A
            prix_b: Série de prix de l'action B
            ratio: Ratio de couverture (hedge ratio)
            
        Returns:
            Série du spread calculé
        """
        if len(prix_a) != len(prix_b):
            raise ValueError("Les séries de prix doivent avoir la même longueur")
        
        # Calcul du spread: Prix_A - ratio * Prix_B
        spread = prix_a - ratio * prix_b
        
        return spread
    
    
    def calculer_zscore(self, spread: pd.Series, window: int = 20) -> pd.Series:
        """
        Calcule le z-score du spread sur une fenêtre glissante.
        
        Le z-score mesure le nombre d'écarts-types du spread
        par rapport à sa moyenne mobile.
        
        Args:
            spread: Série du spread
            window: Taille de la fenêtre glissante (défaut: 20 jours)
            
        Returns:
            Série du z-score calculé
        """
        if window > len(spread):
            raise ValueError(f"La fenêtre ({window}) ne peut pas être supérieure à la longueur du spread ({len(spread)})")
        
        # Calcul de la moyenne mobile
        moyenne_mobile = spread.rolling(window=window).mean()
        
        # Calcul de l'écart-type mobile
        ecart_type_mobile = spread.rolling(window=window).std()
        
        # Calcul du z-score: (spread - moyenne) / écart-type
        zscore = (spread - moyenne_mobile) / ecart_type_mobile
        
        return zscore
    
    
    def generer_signaux(self, zscore: pd.Series) -> pd.DataFrame:
        """
        Génère les signaux d'entrée et de sortie de position.
        
        Logique des signaux:
        - Signal = 1 (LONG): Z-score < -seuil_entree → Acheter A, vendre B
        - Signal = -1 (SHORT): Z-score > +seuil_entree → Vendre A, acheter B
        - Signal = 0 (NEUTRE): |Z-score| < seuil_sortie → Sortir de position
        
        Args:
            zscore: Série du z-score
            
        Returns:
            DataFrame avec colonnes:
                - zscore: Valeur du z-score
                - signal: Signal de position (1, -1, ou 0)
                - position: Position active (maintenue jusqu'au signal de sortie)
        """
        df_signaux = pd.DataFrame(index=zscore.index)
        df_signaux['zscore'] = zscore
        
        # Initialisation des colonnes
        df_signaux['signal'] = 0
        df_signaux['position'] = 0
        
        # Génération des signaux
        # LONG: Z-score très négatif (spread sous-évalué)
        df_signaux.loc[zscore < -self.seuil_entree, 'signal'] = 1
        
        # SHORT: Z-score très positif (spread sur-évalué)
        df_signaux.loc[zscore > self.seuil_entree, 'signal'] = -1
        
        # SORTIE: Z-score revient vers la moyenne
        df_signaux.loc[abs(zscore) < self.seuil_sortie, 'signal'] = 0
        
        # Calculer la position active (forward fill jusqu'au prochain signal)
        position_actuelle = 0
        positions = []
        
        for signal in df_signaux['signal']:
            if signal != 0:
                position_actuelle = signal
            positions.append(position_actuelle)
        
        df_signaux['position'] = positions
        
        return df_signaux
    
    
    def simuler_trades(self, df_signaux: pd.DataFrame, prix_a: pd.Series, prix_b: pd.Series, ratio: float) -> pd.DataFrame:
        """
        Simule l'exécution des trades et calcule les profits/pertes.
        
        Args:
            df_signaux: DataFrame des signaux (retour de generer_signaux)
            prix_a: Série de prix de l'action A
            prix_b: Série de prix de l'action B
            ratio: Ratio de couverture
            
        Returns:
            DataFrame avec colonnes:
                - position: Position active
                - pnl_quotidien: Profit/perte quotidien
                - pnl_cumule: Profit/perte cumulé
                - capital: Valeur du capital
        """
        df_trades = df_signaux.copy()
        df_trades['prix_a'] = prix_a
        df_trades['prix_b'] = prix_b
        
        # Calcul des rendements quotidiens
        df_trades['rendement_a'] = prix_a.pct_change()
        df_trades['rendement_b'] = prix_b.pct_change()
        
        # PnL quotidien basé sur la position
        # LONG (position=1): Profit si A monte et B baisse
        # SHORT (position=-1): Profit si A baisse et B monte
        df_trades['pnl_quotidien'] = (
            df_trades['position'].shift(1) * df_trades['rendement_a'] -
            df_trades['position'].shift(1) * ratio * df_trades['rendement_b']
        ) * self.capital_initial
        
        # Remplacer NaN par 0
        df_trades['pnl_quotidien'] = df_trades['pnl_quotidien'].fillna(0)
        
        # Calcul du PnL cumulé
        df_trades['pnl_cumule'] = df_trades['pnl_quotidien'].cumsum()
        
        # Calcul du capital
        df_trades['capital'] = self.capital_initial + df_trades['pnl_cumule']
        
        return df_trades
    
    
    def calculer_metriques(self, df_trades: pd.DataFrame) -> Dict[str, float]:
        """
        Calcule les métriques de performance de la stratégie.
        
        Args:
            df_trades: DataFrame des trades (retour de simuler_trades)
            
        Returns:
            Dictionnaire avec les métriques:
                - rendement_total: Rendement total en %
                - sharpe_ratio: Ratio de Sharpe annualisé
                - max_drawdown: Drawdown maximal en %
                - win_rate: Taux de trades gagnants en %
                - nombre_trades: Nombre total de trades
        """
        # Rendement total
        rendement_total = (
            (df_trades['capital'].iloc[-1] - self.capital_initial) / 
            self.capital_initial * 100
        )
        
        # Sharpe Ratio (annualisé, suppose 252 jours de trading)
        rendements_quotidiens = df_trades['pnl_quotidien'] / self.capital_initial
        if rendements_quotidiens.std() > 0:
            sharpe_ratio = (
                rendements_quotidiens.mean() / rendements_quotidiens.std() * 
                np.sqrt(252)
            )
        else:
            sharpe_ratio = 0.0
        
        # Maximum Drawdown
        capital_max = df_trades['capital'].cummax()
        drawdown = (df_trades['capital'] - capital_max) / capital_max * 100
        max_drawdown = drawdown.min()
        
        # Win Rate
        trades_gagnants = (df_trades['pnl_quotidien'] > 0).sum()
        trades_perdants = (df_trades['pnl_quotidien'] < 0).sum()
        total_trades = trades_gagnants + trades_perdants
        
        if total_trades > 0:
            win_rate = trades_gagnants / total_trades * 100
        else:
            win_rate = 0.0
        
        # Nombre de changements de position (trades)
        changements_position = (df_trades['position'] != df_trades['position'].shift(1)).sum()
        nombre_trades = changements_position - 1  # Exclure le premier changement
        
        return {
            'rendement_total': round(rendement_total, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'max_drawdown': round(max_drawdown, 2),
            'win_rate': round(win_rate, 2),
            'nombre_trades': int(nombre_trades)
        }