"""Module FeatureEngineer pour la création de features ML."""

import pandas as pd
import numpy as np


class FeatureEngineer:
    """
    Crée les features nécessaires aux modèles ML
    à partir des données de prix d'une paire.
    """

    def __init__(self, feature_config: dict = None):
        """
        Initialise le FeatureEngineer.

        Args:
            feature_config (dict): Configuration des features
                (fenêtres, paramètres). Si None, valeurs par défaut.
        """
        self.feature_config = feature_config or {
            'fenetre_rsi': 14,
            'fenetre_bollinger': 20,
            'fenetre_volatilite': 20,
            'fenetre_correlation': 30,
        }

    def calculer_rsi(self, prix: pd.Series, fenetre: int = 14) -> pd.Series:
        """Calcule le Relative Strength Index (RSI) d'une série de prix.

        Args:
            prix (pd.Series): Série de prix de l'actif.
            fenetre (int): Fenêtre de calcul en jours (défaut: 14).

        Returns:
            pd.Series: Série du RSI entre 0 et 100.
                Les premières valeurs (fenetre) seront NaN.
                Si moyenne_pertes vaut 0, le RSI vaut 100 (comportement attendu).
        """
        # 1. Variations journalières
        delta = prix.diff()

        # 2. Séparation des gains et des pertes
        gains = delta.where(delta > 0, 0)
        pertes = delta.where(delta <0, 0).abs()

        # 3. Moyennes glissantes
        moyenne_gains = gains.rolling(window=fenetre).mean()
        moyenne_pertes = pertes.rolling(window=fenetre).mean()

        # 4. Calcul du RSI
        rs = moyenne_gains / moyenne_pertes
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculer_bollinger(self, prix: pd.Series, fenetre: int = 20) -> pd.DataFrame:
        """Calcule les Bandes de Bollinger d'une série de prix.

        Args:
            prix (pd.Series): Série de prix de l'actif.
            fenetre (int): Fenêtre de calcul en jours (défaut: 20).

        Returns:
            pd.DataFrame: DataFrame avec trois colonnes :
                - bb_upper : Bande supérieure (moyenne + 2 * écart-type)
                - bb_middle : Bande médiane (moyenne mobile)
                - bb_lower : Bande inférieure (moyenne - 2 * écart-type)
                Les premières valeurs (fenetre) seront NaN.
        """
        # 1. Moyenne glissante (Bande centrale)
        moyenne = prix.rolling(window=fenetre).mean()

        # 2. Volatilité (Écart-type)
        ecart_type = prix.rolling(window=fenetre).std()
        bb_upper = moyenne + (2 * ecart_type)
        bb_lower = moyenne - (2 * ecart_type)

        return pd.DataFrame({
            'bb_upper': bb_upper,
            'bb_middle': moyenne,
            'bb_lower': bb_lower
        })

    def calculate_volatility(self, prix: pd.Series, fenetre: int = 20) -> pd.Series:
        """Calcule la volatilité glissante annualisée d'une série de prix.

        Args:
            prix (pd.Series): Série de prix de l'actif.
            fenetre (int): Fenêtre de calcul en jours (défaut: 20).

        Returns:
            pd.Series: Volatilité annualisée (écart-type des rendements * √252).
                Les premières valeurs (fenetre) seront NaN.
        """
        # 1. Calcul des rendements quotidiens
        rendement = prix.pct_change()
        # 2. Écart-type glissant (Volatilité quotidienne)
        volatilite_quotidienne = rendement.rolling(window=fenetre).std()
        # 3. Annualisation et retour
        return volatilite_quotidienne * (252 ** 0.5)
    
    def calculate_rolling_correlation(self, a: pd.Series, b: pd.Series, fenetre: int = 30) -> pd.Series:
        """Calcule la corrélation glissante entre deux séries de prix.

        Args:
            a (pd.Series): Première série de prix.
            b (pd.Series): Deuxième série de prix.
            fenetre (int): Fenêtre de calcul en jours (défaut: 30).

        Returns:
            pd.Series: Corrélation glissante entre -1 et 1.
                Les premières valeurs (fenetre) seront NaN.
        """
        return a.rolling(window=fenetre).corr(b)

    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcule les indicateurs techniques et les ajoute au DataFrame.

        Args:
            df (pd.DataFrame): DataFrame avec au minimum une colonne 'Close'.

        Returns:
            pd.DataFrame: DataFrame enrichi avec les colonnes :
                - rsi : Relative Strength Index
                - bb_upper : Bande de Bollinger supérieure
                - bb_middle : Bande de Bollinger médiane
                - bb_lower : Bande de Bollinger inférieure
        """
        df = df.copy()
        # 1. Calcul et ajout du RSI directement dans df
        df['rsi'] = self.calculer_rsi(df['Close'])
        # 2. Calcul des Bandes de Bollinger (stocké dans un tableau temporaire)
        bollinger_df = self.calculer_bollinger(df['Close'])
        # 3. Rapatriement des bandes dans le tableau principal df
        df['bb_upper'] = bollinger_df['bb_upper']
        df['bb_middle'] = bollinger_df['bb_middle']
        df['bb_lower'] = bollinger_df['bb_lower']
        return df

    def create_ml_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Crée toutes les features ML à partir des données de prix.

        Orchestre le calcul de tous les indicateurs et retourne un DataFrame
        prêt à être utilisé par le modèle XGBoost. Les lignes contenant des
        NaN (dues aux fenêtres glissantes) sont supprimées.

        Args:
            df (pd.DataFrame): DataFrame avec au minimum les colonnes
                'Close', 'spread', 'zscore'.

        Returns:
            pd.DataFrame: DataFrame nettoyé avec les colonnes :
                - rsi, bb_upper, bb_middle, bb_lower (indicateurs techniques)
                - volatilite (volatilité annualisée glissante)
                - spread, zscore (conservés tels quels)
        """
        df = df.copy()
        # 1. Ajout des indicateurs techniques (RSI, Bollinger)
        df = self.calculate_technical_indicators(df)
        # 2. Ajout de la volatilité
        df['volatilite'] = self.calculate_volatility(df['Close'])
        # 3. Nettoyage des valeurs manquantes dues aux fenêtres glissantes
        df = df.dropna()
        return df