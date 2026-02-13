"""Module Backtester pour la simulation de stratégies de pairs trading."""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
from backend.app.core.strategies import Strategy


class Backtester:
    """
    Classe responsable de la simulation de stratégies de pairs trading
    sur données historiques et du calcul des métriques de performance.
    Le Backtester est un moteur d'exécution qui délègue la génération
    des signaux à une Strategy injectée.
    """
    
    def __init__(self, strategy: Strategy, capital_initial: float = 10000.0):
        """
        Initialise le Backtester.
        
        Args:
            strategy: Instance de Strategy pour générer les signaux
            capital_initial: Capital de départ en euros (défaut: 10000.0)
        """
        self.strategy = strategy
        self.capital_initial = capital_initial

    
    def executer_backtest(self, prix_a: pd.Series, prix_b: pd.Series) -> Dict:
        """
        Exécute un backtest complet sur une paire d'actions.
        
        Args:
            prix_a: Série de prix de l'action A
            prix_b: Série de prix de l'action B
            
        Returns:
            Dictionnaire contenant:
                - df_signaux: DataFrame des signaux générés
                - df_trades: DataFrame des trades simulés
                - metriques: Dictionnaire des métriques de performance
                - ratio: Ratio de couverture utilisé
        """

        # Génération des signaux (délégué à la stratégie)
        df_signaux = self.strategy.generer_signaux(prix_a, prix_b)
        # Extraction du ratio
        ratio = df_signaux['ratio'].iloc[0]
        # Simuler des trades
        df_trades = self.simuler_trades(df_signaux, prix_a, prix_b, ratio)
        # Calcul des métriques
        metriques = self.calculer_metriques(df_trades)
        return {
            'df_signaux': df_signaux,
            'df_trades': df_trades,
            'metriques': metriques,
            'ratio': ratio
        }
    
    
    def simuler_trades(self, df_signaux: pd.DataFrame, prix_a: pd.Series, prix_b: pd.Series, ratio: float) -> pd.DataFrame:
        """
        Simule l'exécution des trades et calcule les profits/pertes.
        
        Args:
            df_signaux: DataFrame des signaux (retour de strategy.generer_signaux)
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
        capital_maximum = df_trades['capital'].cummax()
        drawdown = (df_trades['capital'] - capital_maximum) / capital_maximum * 100
        max_drawdown = drawdown.min()
        
        # Win Rate
        nb_trades_gagnants = (df_trades['pnl_quotidien'] > 0).sum()
        nb_trades_perdants = (df_trades['pnl_quotidien'] < 0).sum()
        nb_trades_total = nb_trades_gagnants + nb_trades_perdants
        
        if nb_trades_total > 0:
            win_rate = nb_trades_gagnants / nb_trades_total * 100
        else:
            win_rate = 0.0
        
        # Nombre de changements de position (trades)
        nb_changements_position = (df_trades['position'] != df_trades['position'].shift(1)).sum()
        nombre_trades = nb_changements_position - 1  # Exclure le premier changement
        
        return {
            'rendement_total': round(rendement_total, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'max_drawdown': round(max_drawdown, 2),
            'win_rate': round(win_rate, 2),
            'nombre_trades': int(nombre_trades)
        }