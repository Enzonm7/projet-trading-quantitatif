"""
Tests unitaires pour le module DatasetBuilder.
Pattern AAA (Arrange-Act-Assert) pour tous les tests.
"""

import pytest
import pandas as pd
import numpy as np
from backend.app.ml.feature_engineer import FeatureEngineer
from backend.app.ml.dataset_builder import DatasetBuilder


class TestDatasetBuilder:
    """Tests du DatasetBuilder."""

    # ==================== FIXTURES ====================

    @pytest.fixture
    def df_prix(self):
        """Fixture : DataFrame de prix synthétiques avec les colonnes requises."""
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=200, freq='D')
        prix = pd.Series(np.random.randn(200).cumsum() + 100, index=dates)
        return pd.DataFrame({
            'Close': prix,
            'spread': np.random.randn(200),
            'zscore': np.random.randn(200),
        }, index=dates)

    @pytest.fixture
    def preparateur(self):
        """Fixture : Instance de DatasetBuilder avec FeatureEngineer injecté."""
        engineer = FeatureEngineer()
        return DatasetBuilder(feature_engineer=engineer, horizon=5)

    @pytest.fixture
    def df_labellise(self, preparateur, df_prix):
        """Fixture : DataFrame après feature engineering et labellisation."""
        df_features = preparateur.feature_engineer.create_ml_features(df_prix)
        return preparateur.labelliser_convergence(df_features)

    # ==================== TESTS LABELLISER_CONVERGENCE ====================

    def test_labelliser_convergence_retourne_dataframe(self, preparateur, df_prix):
        """Vérifie que labelliser_convergence() retourne un DataFrame."""
        # ARRANGE
        df_features = preparateur.feature_engineer.create_ml_features(df_prix)
        # ACT
        df_labellise = preparateur.labelliser_convergence(df_features)
        # ASSERT
        assert isinstance(df_labellise, pd.DataFrame)

    def test_labelliser_convergence_colonne_target(self, preparateur, df_prix):
        """Vérifie que la colonne 'target' est présente après labellisation."""
        # ARRANGE
        df_features = preparateur.feature_engineer.create_ml_features(df_prix)
        # ACT
        df_labellise = preparateur.labelliser_convergence(df_features)
        # ASSERT
        assert 'target' in df_labellise.columns

    def test_labelliser_convergence_valeurs_binaires(self, preparateur, df_prix):
        """Vérifie que la colonne 'target' ne contient que des 0 et des 1."""
        # ARRANGE
        df_features = preparateur.feature_engineer.create_ml_features(df_prix)
        # ACT
        df_labellise = preparateur.labelliser_convergence(df_features)
        # ASSERT
        valeurs_uniques = set(df_labellise['target'].unique())
        assert valeurs_uniques.issubset({0, 1})

    def test_labelliser_convergence_sans_nan(self, preparateur, df_prix):
        """Vérifie qu'il n'y a pas de NaN dans le DataFrame labellisé."""
        # ARRANGE
        df_features = preparateur.feature_engineer.create_ml_features(df_prix)
        # ACT
        df_labellise = preparateur.labelliser_convergence(df_features)
        # ASSERT
        assert df_labellise.isna().sum().sum() == 0

    def test_labelliser_convergence_reduit_lignes(self, preparateur, df_prix):
        """Vérifie que labelliser_convergence() supprime les dernières lignes (horizon)."""
        # ARRANGE
        df_features = preparateur.feature_engineer.create_ml_features(df_prix)
        nb_lignes_avant = len(df_features)
        # ACT
        df_labellise = preparateur.labelliser_convergence(df_features)
        # ASSERT
        assert len(df_labellise) < nb_lignes_avant

    def test_labelliser_convergence_ne_modifie_pas_original(self, preparateur, df_prix):
        """Vérifie que le DataFrame original n'est pas modifié."""
        # ARRANGE
        df_features = preparateur.feature_engineer.create_ml_features(df_prix)
        df_original = df_features.copy()
        # ACT
        preparateur.labelliser_convergence(df_features)
        # ASSERT
        pd.testing.assert_frame_equal(df_features, df_original)

    # ==================== TESTS SPLITTER_TEMPOREL ====================

    def test_splitter_temporel_retourne_trois_dataframes(self, preparateur, df_labellise):
        """Vérifie que splitter_temporel() retourne bien un tuple de 3 DataFrames."""
        # ACT
        df_train, df_val, df_test = preparateur.splitter_temporel(df_labellise)
        # ASSERT
        assert isinstance(df_train, pd.DataFrame)
        assert isinstance(df_val, pd.DataFrame)
        assert isinstance(df_test, pd.DataFrame)

    def test_splitter_temporel_taille_train(self, preparateur, df_labellise):
        """Vérifie que le split train représente environ 70% des données."""
        # ARRANGE
        nb_total = len(df_labellise)
        # ACT
        df_train, _, _ = preparateur.splitter_temporel(df_labellise)
        # ASSERT
        assert len(df_train) == int(nb_total * 0.70)

    def test_splitter_temporel_taille_val(self, preparateur, df_labellise):
        """Vérifie que le split validation représente environ 15% des données."""
        # ARRANGE
        nb_total = len(df_labellise)
        # ACT
        _, df_val, _ = preparateur.splitter_temporel(df_labellise)
        # ASSERT
        assert len(df_val) == int(nb_total * 0.85) - int(nb_total * 0.70)

    def test_splitter_temporel_ordre_chronologique(self, preparateur, df_labellise):
        """Vérifie que train précède val qui précède test dans le temps."""
        # ACT
        df_train, df_val, df_test = preparateur.splitter_temporel(df_labellise)
        # ASSERT
        assert df_train.index[-1] < df_val.index[0]
        assert df_val.index[-1] < df_test.index[0]

    def test_splitter_temporel_somme_lignes(self, preparateur, df_labellise):
        """Vérifie que la somme des trois splits égale le total."""
        # ARRANGE
        nb_total = len(df_labellise)
        # ACT
        df_train, df_val, df_test = preparateur.splitter_temporel(df_labellise)
        # ASSERT
        assert len(df_train) + len(df_val) + len(df_test) == nb_total

    # ==================== TESTS PREPARER_DATASET ====================

    def test_preparer_dataset_retourne_trois_dataframes(self, preparateur, df_prix):
        """Vérifie que preparer_dataset() retourne un tuple de 3 DataFrames."""
        # ACT
        df_train, df_val, df_test = preparateur.preparer_dataset(df_prix)
        # ASSERT
        assert isinstance(df_train, pd.DataFrame)
        assert isinstance(df_val, pd.DataFrame)
        assert isinstance(df_test, pd.DataFrame)

    def test_preparer_dataset_colonne_target_presente(self, preparateur, df_prix):
        """Vérifie que la colonne 'target' est présente dans chaque split."""
        # ACT
        df_train, df_val, df_test = preparateur.preparer_dataset(df_prix)
        # ASSERT
        assert 'target' in df_train.columns
        assert 'target' in df_val.columns
        assert 'target' in df_test.columns

    def test_preparer_dataset_sans_nan(self, preparateur, df_prix):
        """Vérifie qu'aucun split ne contient de NaN."""
        # ACT
        df_train, df_val, df_test = preparateur.preparer_dataset(df_prix)
        # ASSERT
        assert df_train.isna().sum().sum() == 0
        assert df_val.isna().sum().sum() == 0
        assert df_test.isna().sum().sum() == 0

    def test_preparer_dataset_ne_modifie_pas_original(self, preparateur, df_prix):
        """Vérifie que le DataFrame original n'est pas modifié."""
        # ARRANGE
        df_original = df_prix.copy()
        # ACT
        preparateur.preparer_dataset(df_prix)
        # ASSERT
        pd.testing.assert_frame_equal(df_prix, df_original)