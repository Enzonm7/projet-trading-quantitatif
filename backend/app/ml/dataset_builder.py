"""Module DatasetBuilder pour la préparation des données ML du pipeline pairs trading."""

import pandas as pd
from backend.app.ml.feature_engineer import FeatureEngineer

class DatasetBuilder:
    """
    Prépare les données brutes en dataset supervisé pour l'entraînement XGBoost.
    """
    
    def __init__(self, feature_engineer: FeatureEngineer, horizon: int = 5):
        """
        Initialise le DatasetBuilder avec ses dépendances.

        Args:
            feature_engineer (FeatureEngineer): Instance de FeatureEngineer
                utilisée pour créer les features ML.
            horizon (int): Nombre de jours forward-looking pour la
                labellisation. Par défaut 5 jours.
        """
        self.feature_engineer = feature_engineer
        self.horizon = horizon

    def labelliser_convergence(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Crée la colonne cible binaire basée sur la convergence future du z-score.
        Pour chaque jour t, compare la valeur absolue du z-score à t+horizon
        avec celle à t. Si le z-score se rapproche de 0, le label est 1
        (convergence), sinon 0 (divergence).

        Args:
            df (pd.DataFrame): DataFrame avec au minimum une colonne 'zscore'.

        Returns:
            pd.DataFrame: DataFrame avec la colonne 'target' ajoutée (1=convergence,
                0=divergence) et sans valeurs NaN.
        """
        df = df.copy()
        # Décalage temporel pour obtenir le z-score futur
        df['zscore_futur'] = df['zscore'].shift(-self.horizon)
        df = df.dropna()
        # Label 1 si le z-score se rapproche de 0 (convergence)
        df['target'] = (df['zscore_futur'].abs() < df['zscore'].abs()).astype(int)
        return df

    def splitter_temporel(self, df: pd.DataFrame) -> tuple:
        """
        Découpe le DataFrame en trois splits chronologiques (70% / 15% / 15%).
        Le découpage est strictement temporel (pas de mélange aléatoire) pour
        éviter le data leakage : le modèle ne voit jamais de données futures
        pendant l'entraînement.

        Args:
            df (pd.DataFrame): DataFrame labellisé à découper.

        Returns:
            tuple: (df_train, df_val, df_test) trois DataFrames chronologiquement
                ordonnés représentant respectivement 70%, 15% et 15% des données.
        """
        df = df.copy()
        # 1. Calcul des indices de coupure
        train_idx = int(len(df) * 0.70)
        val_idx = int(len(df) * 0.85)
        # 2. Découpage du DataFrame
        df_train = df.iloc[:train_idx]
        df_val = df.iloc[train_idx:val_idx]
        df_test = df.iloc[val_idx:]
        return (df_train, df_val, df_test)

    def preparer_dataset(self, df: pd.DataFrame) -> tuple:
        """
        Orchestre le pipeline complet de préparation des données ML.

        Args:
            df (pd.DataFrame): DataFrame brut avec les colonnes 'Close',
                'spread' et 'zscore'.

        Returns:
            tuple: (df_train, df_val, df_test) prêts pour l'entraînement XGBoost,
                contenant features et colonne 'target'.
        """
        df = df.copy()
        # 1. Calcul des features ML
        df = self.feature_engineer.create_ml_features(df)
        # 2. Labellisation convergence/divergence
        df = self.labelliser_convergence(df)
        # 3. Découpage temporel
        df_train, df_val, df_test = self.splitter_temporel(df)
        return (df_train, df_val, df_test)