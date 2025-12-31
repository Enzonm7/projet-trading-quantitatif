"""
Module RiskManager pour la gestion du risque et du dimensionnement des positions.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple


class RiskManager:
    """
    Classe responsable de la gestion du risque :
    - Dimensionnement des positions (position sizing)
    - Gestion des stop-loss
    - Contrôle du leverage
    """
    
    def __init__(self, max_position_size: float = 0.1, stop_loss_pct: float = 0.02, max_leverage: float = 1.0):
        """
        Initialise le RiskManager.
        
        Args:
            max_position_size: Taille maximale d'une position en % du capital (défaut: 0.1 = 10%)
            stop_loss_pct: Stop-loss en % du capital (défaut: 0.02 = 2%)
            max_leverage: Effet de levier maximum (défaut: 1.0 = pas de leverage)
        """
        self.max_position_size = max_position_size
        self.stop_loss_pct = stop_loss_pct
        self.max_leverage = max_leverage
    
    
    def calculer_taille_position(self, capital: float, volatilite: float = None) -> float:
        """
        Calcule la taille optimale de la position en euros.
        
        Si la volatilité est fournie, ajuste la taille en fonction du risque.
        Sinon, utilise simplement le pourcentage maximum du capital.
        
        Args:
            capital: Capital disponible en euros
            volatilite: Volatilité de la paire (écart-type des rendements) - optionnel
            
        Returns:
            Taille de la position en euros
        """
        if capital <= 0:
            raise ValueError(f"Le capital doit être positif (capital = {capital})")
        
        # Taille de base : pourcentage fixe du capital
        taille_base = capital * self.max_position_size
        
        # Si volatilité fournie, ajuster la taille (plus de volatilité = position plus petite)
        if volatilite is not None and volatilite > 0:
            # Facteur d'ajustement : 1 / volatilité normalisée
            # Plus la volatilité est élevée, plus le facteur est faible
            facteur_ajustement = 1 / (1 + volatilite * 10)  # 10 = facteur de sensibilité
            taille_ajustee = taille_base * facteur_ajustement
            return taille_ajustee
        
        return taille_base
    
    
    def verifier_stop_loss(self, capital_initial: float, capital_actuel: float) -> Tuple[bool, float]:
        """
        Vérifie si le stop-loss global a été déclenché.
        
        Le stop-loss est déclenché si la perte dépasse le pourcentage maximum
        autorisé par rapport au capital initial.
        
        Args:
            capital_initial: Capital de départ
            capital_actuel: Capital actuel
            
        Returns:
            Tuple (stop_loss_declenche, perte_pct):
                - stop_loss_declenche: True si stop-loss atteint, False sinon
                - perte_pct: Perte en pourcentage du capital initial
        """
        # Calcul de la perte en pourcentage
        perte_pct = (capital_initial - capital_actuel) / capital_initial
        
        # Vérifier si le stop-loss est déclenché
        stop_loss_declenche = perte_pct >= self.stop_loss_pct
        
        return (stop_loss_declenche, perte_pct)
    
    
    def verifier_stop_loss_position(self, prix_entree: float, prix_actuel: float, type_position: int, max_perte_pct: float = 0.05) -> bool:
        """
        Vérifie si le stop-loss d'une position individuelle est déclenché.
        
        Args:
            prix_entree: Prix d'entrée de la position
            prix_actuel: Prix actuel
            type_position: Type de position (1 = LONG, -1 = SHORT)
            max_perte_pct: Perte maximale autorisée en % (défaut: 5%)
            
        Returns:
            True si stop-loss déclenché, False sinon
        """
        if type_position == 1:  # Position LONG
            perte_pct = (prix_entree - prix_actuel) / prix_entree
        elif type_position == -1:  # Position SHORT
            perte_pct = (prix_actuel - prix_entree) / prix_entree
        else:
            return False  # Pas de position
        
        return perte_pct >= max_perte_pct
    
    
    def ajuster_leverage(self, sharpe_ratio: float, capital: float) -> float:
        """
        Ajuste dynamiquement le leverage en fonction du Sharpe Ratio.
        
        Un Sharpe Ratio élevé indique une stratégie performante,
        permettant d'augmenter le leverage jusqu'à la limite maximale.
        
        Args:
            sharpe_ratio: Ratio de Sharpe de la stratégie
            capital: Capital disponible
            
        Returns:
            Leverage ajusté (entre 1.0 et max_leverage)
        """
        # Leverage de base = 1 (pas de leverage)
        leverage_base = 1.0
        
        # Si Sharpe Ratio > 1, on peut augmenter le leverage progressivement
        if sharpe_ratio > 1.0:
            # Formule simple : leverage = 1 + (Sharpe - 1) * 0.5
            # Ex: Sharpe = 2 → leverage = 1.5
            #     Sharpe = 3 → leverage = 2.0
            leverage_ajuste = leverage_base + (sharpe_ratio - 1) * 0.5
            
            # Limiter au leverage maximum autorisé
            leverage_final = min(leverage_ajuste, self.max_leverage)
        else:
            # Si Sharpe < 1, pas de leverage
            leverage_final = leverage_base
        
        return leverage_final
    
    
    def appliquer_gestion_risque(self, df_trades: pd.DataFrame, capital_initial: float, prix_a: pd.Series, prix_b: pd.Series) -> pd.DataFrame:
        """
        Applique les règles de gestion du risque aux trades simulés.
        
        Ajoute des colonnes pour :
        - Stop-loss global déclenché
        - Stop-loss par position
        - Taille de position ajustée
        
        Args:
            df_trades: DataFrame des trades (sortie de Backtester.simuler_trades)
            capital_initial: Capital de départ
            prix_a: Série de prix de l'action A
            prix_b: Série de prix de l'action B
            
        Returns:
            DataFrame enrichi avec colonnes de gestion du risque
        """
        df_risk = df_trades.copy()
        
        # Initialiser les colonnes
        df_risk['stop_loss_global'] = False
        df_risk['stop_loss_position'] = False
        df_risk['taille_position'] = 0.0
        
        # Suivre le prix d'entrée pour chaque position
        prix_entree_a = None
        type_position_active = 0
        
        for idx in df_risk.index:
            capital_actuel = df_risk.loc[idx, 'capital']
            position = df_risk.loc[idx, 'position']
            
            # Vérifier stop-loss global
            stop_global, perte_pct = self.verifier_stop_loss(capital_initial, capital_actuel)
            df_risk.loc[idx, 'stop_loss_global'] = stop_global
            
            # Si stop-loss global déclenché, fermer toutes les positions
            if stop_global:
                df_risk.loc[idx:, 'position'] = 0
                break
            
            # Détecter changement de position (entrée en trade)
            if position != 0 and position != type_position_active:
                # Nouvelle position : enregistrer prix d'entrée
                prix_entree_a = prix_a.loc[idx]
                type_position_active = position
                
                # Calculer taille de position
                volatilite = df_trades['pnl_quotidien'].std() / capital_initial
                taille = self.calculer_taille_position(capital_actuel, volatilite)
                df_risk.loc[idx, 'taille_position'] = taille
            
            # Vérifier stop-loss de la position active
            if position != 0 and prix_entree_a is not None:
                prix_actuel_a = prix_a.loc[idx]
                stop_position = self.verifier_stop_loss_position(
                    prix_entree_a, 
                    prix_actuel_a, 
                    type_position_active,
                    max_perte_pct=0.05
                )
                df_risk.loc[idx, 'stop_loss_position'] = stop_position
                
                # Si stop-loss position déclenché, fermer la position
                if stop_position:
                    df_risk.loc[idx:, 'position'] = 0
                    prix_entree_a = None
                    type_position_active = 0
            
            # Si position fermée, réinitialiser
            if position == 0:
                prix_entree_a = None
                type_position_active = 0
        
        return df_risk
    
    
    def calculer_metriques_risque(self, df_trades: pd.DataFrame, capital_initial: float) -> Dict[str, float]:
        """
        Calcule les métriques de risque de la stratégie.
        
        Args:
            df_trades: DataFrame des trades
            capital_initial: Capital de départ
            
        Returns:
            Dictionnaire avec métriques de risque:
                - perte_max: Perte maximale en euros
                - perte_max_pct: Perte maximale en %
                - volatilite_quotidienne: Volatilité des rendements quotidiens
                - var_95: Value at Risk à 95%
                - ratio_gain_perte: Ratio gain moyen / perte moyenne
        """
        # Perte maximale
        capital_min = df_trades['capital'].min()
        perte_max = capital_initial - capital_min
        perte_max_pct = (perte_max / capital_initial) * 100
        
        # Volatilité quotidienne
        rendements = df_trades['pnl_quotidien'] / capital_initial
        volatilite_quotidienne = rendements.std()
        
        # Value at Risk (VaR) à 95%
        var_95 = rendements.quantile(0.05)
        
        # Ratio gain/perte
        gains = df_trades[df_trades['pnl_quotidien'] > 0]['pnl_quotidien']
        pertes = df_trades[df_trades['pnl_quotidien'] < 0]['pnl_quotidien']
        
        if len(gains) > 0 and len(pertes) > 0:
            gain_moyen = gains.mean()
            perte_moyenne = abs(pertes.mean())
            ratio_gain_perte = gain_moyen / perte_moyenne if perte_moyenne > 0 else 0
        else:
            ratio_gain_perte = 0.0
        
        return {
            'perte_max': round(perte_max, 2),
            'perte_max_pct': round(perte_max_pct, 2),
            'volatilite_quotidienne': round(volatilite_quotidienne * 100, 4),
            'var_95': round(var_95 * 100, 4),
            'ratio_gain_perte': round(ratio_gain_perte, 2)
        }