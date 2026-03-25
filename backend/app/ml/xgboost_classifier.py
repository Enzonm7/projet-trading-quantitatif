"""Module XGBoostClassifier pour la prédiction de convergence/divergence du spread."""

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.preprocessing import StandardScaler

class XGBoostClassifier:
    """
    Classifieur XGBoost pour prédire la convergence (1) ou divergence (0) du spread.
    """

    def __init__(self, model_config: dict = None):
        self.model_config = model_config or {
            'n_estimators': 100,
            'max_depth': 4,
            'learning_rate': 0.1,
            'random_state': 42,
        }
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None

    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Entraîne le modèle XGBoost sur les données fournies.

        Args:
            X (np.ndarray | pd.DataFrame): Matrice de features d'entraînement.
                Si DataFrame, les noms de colonnes sont sauvegardés pour get_feature_importance().
            y (np.ndarray): Vecteur cible binaire (1 = convergence, 0 = divergence).
        """
        if isinstance(X, pd.DataFrame):
            self.feature_names = X.columns.tolist()
        else : 
            self.feature_names = None
        # Mise à l'échelle (Standardisation)
        x_scaled = self.scaler.fit_transform(X)
        # Instanciation du modèle avec unpacking du dictionnaire
        self.model = xgb.XGBClassifier(**self.model_config)
        # Entraînement de l'algorithme
        self.model.fit(x_scaled, y)
        

    def predict(self, X: np.ndarray) -> np.ndarray:
        """..."""

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """..."""

    def get_feature_importance(self) -> pd.Series:
        """..."""