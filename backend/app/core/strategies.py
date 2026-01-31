"""Module Strategy pour extraire la logique de génération de signaux dans une interface."""

import pandas as pd
from abc import ABC, abstractmethod
from scipy import stats

class Strategy(ABC) :
    """
    Interface abstraite pour les stratégies de trading.
    Toute nouvelle stratégie doit hériter de cette classe et implémenter generer_signaux.
    """

    @abstractmethod
    def generer_signaux(self, prix_a: pd.Series, prix_b: pd.Series) -> pd.DataFrame:
        """
        Génère les signaux de trading à partir des prix des deux actifs.
        
        Args:
            prix_a (pd.Series): Historique des prix de l'actif A.
            prix_b (pd.Series): Historique des prix de l'actif B.
            
        Returns:
            pd.DataFrame: DataFrame contenant les colonnes 'zscore', 'signal', etc.
        """
        pass
    
class ZScoreReversionStrategy(Strategy) :
    """
    Stratégie de retour à la moyenne basée sur le Z-Score.
    """

    def __init__(self, window: int = 20, seuil_entree: float = 2.0, seuil_sortie: float = 0.5):
        """
        Initialise la stratégie de Z-Score.

        Args:
            window (int): La fenêtre de temps pour la moyenne mobile et l'écart-type (par défaut 20).
            seuil_entree (float): Le niveau de Z-Score pour déclencher une position (par défaut 2.0).
            seuil_sortie (float): Le niveau de Z-Score pour fermer une position (par défaut 0.5).
        """
        self.window = window
        self.seuil_entree = seuil_entree
        self.seuil_sortie = seuil_sortie

    def generer_signaux(self, prix_a: pd.Series, prix_b: pd.Series) -> pd.DataFrame:
        # Calculer le ratio de couverture (Hedge Ratio)
        slope, intercept = stats.linregress(prix_b, prix_a)[:2]
        ratio = slope

        # Calculer le Spread
        spread = prix_a - ratio * prix_b

        # Calculer le Z-Score
        # Calcul de la moyenne mobile
        moyenne_mobile = spread.rolling(self.window).mean()
        
        # Calcul de l'écart-type mobile
        ecart_type_mobile = spread.rolling(self.window).std()
        zscore = (spread - moyenne_mobile) / ecart_type_mobile

        # Générer les signaux 
        df_signaux = pd.DataFrame(index=zscore.index)
        df_signaux['zscore'] = zscore
        df_signaux['signal'] = 0

        # 1 = Achat du spread, -1 = Vente du spread
        df_signaux.loc[zscore < -self.seuil_entree, 'signal'] = 1
        df_signaux.loc[zscore > self.seuil_entree, 'signal'] = -1

        # Gestion des positions 
        positions = []
        position_actuelle = 0
        
        # On itère pour gérer l'état (je garde ma position tant que je ne touche pas la sortie)
        for i in range(len(df_signaux)):
            sig = df_signaux['signal'].iloc[i]
            zs = df_signaux['zscore'].iloc[i]

            # Si signal d'entrée fort, on prend position
            if sig != 0:
                position_actuelle = sig
            # Sinon, si on est en position, on vérifie si on doit sortir
            elif position_actuelle != 0:
                # Si le Z-Score est revenu dans la bande de sortie (proche de 0)
                if abs(zs) < self.seuil_sortie:
                    position_actuelle = 0

            positions.append(position_actuelle)

        df_signaux['position'] = positions
        df_signaux['spread'] = spread 
        df_signaux['ratio'] = ratio
        
        return df_signaux
        