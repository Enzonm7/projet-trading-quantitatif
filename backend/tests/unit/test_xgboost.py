"""
Tests unitaires pour le module XGBoostClassifier.
Pattern AAA (Arrange-Act-Assert) pour tous les tests.
"""

import pytest
import numpy as np
import pandas as pd
from backend.app.ml.xgboost_classifier import XGBoostClassifier


class TestXGBoostClassifier:
    """Tests du XGBoostClassifier."""

    # ==================== FIXTURES ====================

    @pytest.fixture
    def donnees_entrainement(self):
        """Fixture : Données synthétiques d'entraînement (DataFrame 50x4 + labels binaires)."""
        np.random.seed(42)
        X = pd.DataFrame(
            np.random.randn(50, 4),
            columns=["rsi", "bollinger", "volatilite", "correlation"],
        )
        y = np.array([0, 1] * 25)
        return X, y

    @pytest.fixture
    def classificateur_entraine(self, donnees_entrainement):
        """Fixture : XGBoostClassifier déjà entraîné, prêt à l'emploi."""
        X, y = donnees_entrainement
        clf = XGBoostClassifier()
        clf.train(X, y)
        return clf

    # ==================== TESTS TRAIN ====================

    def test_train_sans_erreur(self, donnees_entrainement):
        """Vérifie que train() s'exécute sans exception sur des données valides."""
        # ARRANGE
        X, y = donnees_entrainement
        clf = XGBoostClassifier()
        # ACT / ASSERT
        clf.train(X, y)

    def test_train_deux_fois_ne_plante_pas(self, donnees_entrainement):
        """Vérifie qu'un second appel à train() ne lève pas d'exception."""
        # ARRANGE
        X, y = donnees_entrainement
        clf = XGBoostClassifier()
        clf.train(X, y)
        # ACT / ASSERT
        clf.train(X, y)

    def test_train_deux_fois_predict_fonctionne(self, donnees_entrainement):
        """Vérifie qu'après ré-entraînement, predict() retourne un résultat valide."""
        # ARRANGE
        X, y = donnees_entrainement
        clf = XGBoostClassifier()
        clf.train(X, y)
        clf.train(X, y)
        # ACT
        predictions = clf.predict(X)
        # ASSERT
        assert len(predictions) == len(X)

    # ==================== TESTS PREDICT ====================

    def test_predict_retourne_ndarray(self, classificateur_entraine, donnees_entrainement):
        """Vérifie que predict() retourne un np.ndarray."""
        # ARRANGE
        X, _ = donnees_entrainement
        # ACT
        predictions = classificateur_entraine.predict(X)
        # ASSERT
        assert isinstance(predictions, np.ndarray)

    def test_predict_longueur_correcte(self, classificateur_entraine, donnees_entrainement):
        """Vérifie que predict() retourne un tableau de la même longueur que X."""
        # ARRANGE
        X, _ = donnees_entrainement
        # ACT
        predictions = classificateur_entraine.predict(X)
        # ASSERT
        assert len(predictions) == len(X)

    def test_predict_valeurs_binaires(self, classificateur_entraine, donnees_entrainement):
        """Vérifie que predict() ne retourne que des 0 et des 1."""
        # ARRANGE
        X, _ = donnees_entrainement
        # ACT
        predictions = classificateur_entraine.predict(X)
        # ASSERT
        valeurs_uniques = set(predictions)
        assert valeurs_uniques.issubset({0, 1})

    def test_predict_avant_train_leve_exception(self):
        """Vérifie que predict() lève une exception si le modèle n'est pas entraîné."""
        # ARRANGE
        clf = XGBoostClassifier()
        X = np.random.randn(10, 4)
        # ACT / ASSERT
        with pytest.raises(Exception):
            clf.predict(X)

    # ==================== TESTS PREDICT_PROBA ====================

    def test_predict_proba_shape_correcte(self, classificateur_entraine, donnees_entrainement):
        """Vérifie que predict_proba() retourne un tableau de shape (n_samples, 2)."""
        # ARRANGE
        X, _ = donnees_entrainement
        # ACT
        probas = classificateur_entraine.predict_proba(X)
        # ASSERT
        assert probas.shape == (len(X), 2)

    def test_predict_proba_valeurs_entre_0_et_1(self, classificateur_entraine, donnees_entrainement):
        """Vérifie que predict_proba() retourne des valeurs comprises entre 0 et 1."""
        # ARRANGE
        X, _ = donnees_entrainement
        # ACT
        probas = classificateur_entraine.predict_proba(X)
        # ASSERT
        assert np.all(probas >= 0)
        assert np.all(probas <= 1)

    # ==================== TESTS GET_FEATURE_IMPORTANCE ====================

    def test_get_feature_importance_retourne_series(self, classificateur_entraine):
        """Vérifie que get_feature_importance() retourne une pd.Series."""
        # ACT
        importance = classificateur_entraine.get_feature_importance()
        # ASSERT
        assert isinstance(importance, pd.Series)

    def test_get_feature_importance_triee_decroissant(self, classificateur_entraine):
        """Vérifie que get_feature_importance() retourne une Series triée par ordre décroissant."""
        # ACT
        importance = classificateur_entraine.get_feature_importance()
        # ASSERT
        valeurs = importance.tolist()
        assert valeurs == sorted(valeurs, reverse=True)

    def test_get_feature_importance_avant_train_leve_exception(self):
        """Vérifie que get_feature_importance() lève une exception si le modèle n'est pas entraîné."""
        # ARRANGE
        clf = XGBoostClassifier()
        # ACT / ASSERT
        with pytest.raises(Exception):
            clf.get_feature_importance()

    # ==================== TESTS OPTIMISER_HYPERPARAMETRES ====================

    @pytest.fixture
    def donnees_tuning(self):
        """Fixture : Données synthétiques suffisantes pour TimeSeriesSplit(n_splits=5)."""
        np.random.seed(42)
        X = pd.DataFrame(
            np.random.randn(100, 4),
            columns=["rsi", "bollinger", "volatilite", "correlation"],
        )
        y = np.array([0, 1] * 50)
        return X, y

    def test_optimiser_retourne_dict(self, donnees_tuning):
        """Vérifie que optimiser_hyperparametres() retourne un dictionnaire."""
        # ARRANGE
        X, y = donnees_tuning
        clf = XGBoostClassifier()
        # ACT
        resultat = clf.optimiser_hyperparametres(X, y)
        # ASSERT
        assert isinstance(resultat, dict)

    def test_optimiser_stocke_meilleurs_params(self, donnees_tuning):
        """Vérifie que self.meilleurs_params est bien renseigné après l'appel."""
        # ARRANGE
        X, y = donnees_tuning
        clf = XGBoostClassifier()
        # ACT
        clf.optimiser_hyperparametres(X, y)
        # ASSERT
        assert clf.meilleurs_params is not None
        assert isinstance(clf.meilleurs_params, dict)

    def test_optimiser_modele_peut_predire(self, donnees_tuning):
        """Vérifie que le modèle ré-entraîné après tuning peut prédire sans erreur."""
        # ARRANGE
        X, y = donnees_tuning
        clf = XGBoostClassifier()
        # ACT
        clf.optimiser_hyperparametres(X, y)
        predictions = clf.predict(X)
        # ASSERT
        assert isinstance(predictions, np.ndarray)
        assert len(predictions) == len(X)

    def test_optimiser_grille_personnalisee(self, donnees_tuning):
        """Vérifie que optimiser_hyperparametres() accepte une grille personnalisée."""
        # ARRANGE
        X, y = donnees_tuning
        clf = XGBoostClassifier()
        grille = {"n_estimators": [50], "max_depth": [3]}
        # ACT
        resultat = clf.optimiser_hyperparametres(X, y, grille_params=grille)
        # ASSERT
        assert resultat["n_estimators"] == 50
        assert resultat["max_depth"] == 3

    def test_optimiser_sauvegarde_feature_names(self, donnees_tuning):
        """Vérifie que feature_names est mis à jour après optimisation sur un DataFrame."""
        # ARRANGE
        X, y = donnees_tuning
        clf = XGBoostClassifier()
        # ACT
        clf.optimiser_hyperparametres(X, y)
        # ASSERT
        assert clf.feature_names == ["rsi", "bollinger", "volatilite", "correlation"]