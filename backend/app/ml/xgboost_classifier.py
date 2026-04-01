"""Module XGBoostClassifier pour la prédiction de convergence/divergence du spread."""

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

class XGBoostClassifier:
    """
    Classifieur XGBoost pour prédire la convergence (1) ou divergence (0) du spread.
    """

    def __init__(self, model_config: dict = None):
        """
        Initialise le XGBoostClassifier.

        Args:
            model_config (dict): Configuration du modèle XGBoost
                (hyperparamètres). Si None, valeurs par défaut.
        """
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
        X_scaled = self.scaler.fit_transform(X)
        # Instanciation du modèle avec unpacking du dictionnaire
        self.model = xgb.XGBClassifier(**self.model_config)
        # Entraînement de l'algorithme
        self.model.fit(X_scaled, y)
        

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Prédit la classe (convergence/divergence) pour chaque observation.

        Args:
            X (np.ndarray | pd.DataFrame): Matrice de features à prédire.

        Returns:
            np.ndarray: Vecteur de prédictions binaires (1 = convergence, 0 = divergence).
        """
        if self.model is None:
            raise ValueError("Il faut d'abord entraîner le model")
        # Mise à l'échelle stricte (sans ré-entraînement du scaler)
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Prédit les probabilités de chaque classe pour chaque observation.

        Args:
            X (np.ndarray | pd.DataFrame): Matrice de features à prédire.

        Returns:
            np.ndarray: Matrice de shape (n_samples, 2) avec les probabilités
                de divergence (colonne 0) et convergence (colonne 1).
        """
        if self.model is None:
            raise ValueError("Il faut d'abord entraîner le model")
        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)

    def get_feature_importance(self) -> pd.Series:
        """
        Retourne l'importance de chaque feature du modèle entraîné.

        Returns:
            pd.Series: Importances triées par ordre décroissant.
                L'index contient les noms des features si disponibles,
                sinon des indices numériques.
        """
        if self.model is None:
            raise ValueError("Le modèle de prédiction n'existe pas. Veuillez lancer .train().")
        return pd.Series(data=self.model.feature_importances_, index=self.feature_names).sort_values(ascending=False)
    
    def optimiser_hyperparametres(self, X_train, y_train, grille_params=None):
        """Optimise les hyperparamètres du modèle par recherche sur grille.

        Args:
            X_train (pd.DataFrame ou np.ndarray): Données d'entraînement.
            y_train (np.ndarray): Labels d'entraînement (0 ou 1).
            grille_params (dict, optional): Grille de paramètres à explorer.
                Si None, une grille par défaut est utilisée.

        Returns:
            dict: Les meilleurs hyperparamètres trouvés par GridSearchCV.
        """
        # 1. Définition de la grille par défaut
        grille_params = grille_params or {
            "n_estimators": [100, 200],
            "max_depth": [3, 5],
            "learning_rate": [0.05, 0.1],
            "subsample": [0.8, 1.0]
        }
        # 2. Mise à l'échelle des données
        X_scalled = self.scaler.fit_transform(X_train)
        # 3. Création de la validation croisée temporelle
        tscv = TimeSeriesSplit(n_splits=5)
        # 4. Configuration du GridSearchCV
        grid_search = GridSearchCV(
            estimator=xgb.XGBClassifier(random_state=42),
            param_grid=grille_params,cv=tscv, scoring='f1'
        )
        # 5. Lancement de la recherche
        grid_search.fit(X_scalled, y_train)
        # 6. Stockage des meilleurs hyperparamètres
        self.meilleurs_params = grid_search.best_params_
        # 7. Ré-entraînement du modèle final sur tout X_train avec ces paramètres
        self.model = xgb.XGBClassifier(**self.meilleurs_params, random_state=42)
        self.model.fit(X_scalled, y_train)
        if isinstance(X_train, pd.DataFrame):
            self.feature_names = list(X_train.columns)
        return self.meilleurs_params
    
    def evaluer(self, X_test, y_test) -> dict:
        """Évalue les performances du modèle sur un jeu de test.

        Args:
            X_test (pd.DataFrame ou np.ndarray): Données de test.
            y_test (np.ndarray): Labels réels (0 = divergence, 1 = convergence).

        Returns:
            dict: Dictionnaire contenant les métriques suivantes :
                - accuracy (float): Taux de bonnes prédictions global.
                - precision (float): Précision sur la classe positive.
                - recall (float): Rappel sur la classe positive.
                - f1 (float): Moyenne harmonique precision/recall.
                - roc_auc (float): Aire sous la courbe ROC.
        """
        # 1. Prédictions binaires (les 0 et les 1)
        y_pred = self.predict(X_test)
        # 2. Prédictions probabilistes (de 0.0 à 1.0)
        y_proba = self.predict_proba(X_test)[:, 1]
        # 3. Calcul des métriques
        metriques = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, zero_division=0),
            "recall": recall_score(y_test, y_pred, zero_division=0),
            "f1": f1_score(y_test, y_pred, zero_division=0),
            "roc_auc": roc_auc_score(y_test, y_proba)
        }
        return metriques