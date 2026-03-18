"""
Tests unitaires pour le module FeatureEngineer.
Pattern AAA (Arrange-Act-Assert) pour tous les tests.
"""

import pytest
import pandas as pd
import numpy as np
from backend.app.ml.feature_engineer import FeatureEngineer


class TestFeatureEngineer:
    """Tests du FeatureEngineer."""

    # ==================== FIXTURES ====================

    @pytest.fixture
    def engineer(self):
        """Fixture : Instance de FeatureEngineer avec config par défaut."""
        return FeatureEngineer()

    @pytest.fixture
    def df_prix(self):
        """Fixture : DataFrame de prix synthétiques."""
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        prix = pd.Series(np.random.randn(100).cumsum() + 100, index=dates)
        return pd.DataFrame({
            'Close': prix,
            'spread': np.random.randn(100),
            'zscore': np.random.randn(100)
        }, index=dates)

    @pytest.fixture
    def serie_prix(self):
        """Fixture : Série de prix simple."""
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        return pd.Series(np.random.randn(100).cumsum() + 100, index=dates)

    # ==================== TESTS RSI ====================

    def test_calculer_rsi_retourne_series(self, engineer, serie_prix):
        """Vérifie que calculer_rsi retourne une Series."""
        # ACT
        rsi = engineer.calculer_rsi(serie_prix)
        # ASSERT
        assert isinstance(rsi, pd.Series)

    def test_calculer_rsi_longueur(self, engineer, serie_prix):
        """Vérifie que le RSI a la même longueur que l'entrée."""
        rsi = engineer.calculer_rsi(serie_prix)
        assert len(rsi) == len(serie_prix)

    def test_calculer_rsi_valeurs_entre_0_et_100(self, engineer, serie_prix):
        """Vérifie que les valeurs RSI sont entre 0 et 100."""
        rsi = engineer.calculer_rsi(serie_prix).dropna()
        assert (rsi >= 0).all() and (rsi <= 100).all()

    def test_calculer_rsi_nan_debut(self, engineer, serie_prix):
        """Vérifie que le RSI contient des NaN au début."""
        rsi = engineer.calculer_rsi(serie_prix, fenetre=14)
        assert rsi.isna().sum() >= 13

    # ==================== TESTS BOLLINGER ====================

    def test_calculer_bollinger_retourne_dataframe(self, engineer, serie_prix):
        """Vérifie que calculer_bollinger retourne un DataFrame."""
        bb = engineer.calculer_bollinger(serie_prix)
        assert isinstance(bb, pd.DataFrame)

    def test_calculer_bollinger_colonnes(self, engineer, serie_prix):
        """Vérifie que le DataFrame contient les trois colonnes attendues."""
        bb = engineer.calculer_bollinger(serie_prix)
        assert set(bb.columns) == {'bb_upper', 'bb_middle', 'bb_lower'}

    def test_calculer_bollinger_ordre(self, engineer, serie_prix):
        """Vérifie que upper >= middle >= lower."""
        bb = engineer.calculer_bollinger(serie_prix).dropna()
        assert (bb['bb_upper'] >= bb['bb_middle']).all()
        assert (bb['bb_middle'] >= bb['bb_lower']).all()

    # ==================== TESTS VOLATILITE ====================

    def test_calculate_volatility_retourne_series(self, engineer, serie_prix):
        """Vérifie que calculate_volatility retourne une Series."""
        vol = engineer.calculate_volatility(serie_prix)
        assert isinstance(vol, pd.Series)

    def test_calculate_volatility_positive(self, engineer, serie_prix):
        """Vérifie que la volatilité est toujours positive."""
        vol = engineer.calculate_volatility(serie_prix).dropna()
        assert (vol >= 0).all()

    def test_calculate_volatility_nan_debut(self, engineer, serie_prix):
        """Vérifie que la volatilité contient des NaN au début."""
        vol = engineer.calculate_volatility(serie_prix, fenetre=20)
        assert vol.isna().sum() >= 19

    # ==================== TESTS CORRELATION ====================

    def test_calculate_rolling_correlation_retourne_series(self, engineer, serie_prix):
        """Vérifie que calculate_rolling_correlation retourne une Series."""
        serie_b = serie_prix * 1.1 + np.random.randn(100)
        corr = engineer.calculate_rolling_correlation(serie_prix, serie_b)
        assert isinstance(corr, pd.Series)

    def test_calculate_rolling_correlation_entre_moins1_et_1(self, engineer, serie_prix):
        """Vérifie que la corrélation est entre -1 et 1."""
        serie_b = serie_prix * 1.1 + np.random.randn(100)
        corr = engineer.calculate_rolling_correlation(serie_prix, serie_b).dropna()
        assert (corr >= -1).all() and (corr <= 1).all()

    # ==================== TESTS CREATE_ML_FEATURES ====================

    def test_create_ml_features_retourne_dataframe(self, engineer, df_prix):
        """Vérifie que create_ml_features retourne un DataFrame."""
        df = engineer.create_ml_features(df_prix)
        assert isinstance(df, pd.DataFrame)

    def test_create_ml_features_colonnes_requises(self, engineer, df_prix):
        """Vérifie que toutes les features ML sont présentes."""
        colonnes_requises = ['rsi', 'bb_upper', 'bb_middle', 'bb_lower', 'volatilite', 'spread', 'zscore']
        df = engineer.create_ml_features(df_prix)
        for col in colonnes_requises:
            assert col in df.columns, f"Colonne manquante: {col}"

    def test_create_ml_features_sans_nan(self, engineer, df_prix):
        """Vérifie que le DataFrame final ne contient pas de NaN."""
        df = engineer.create_ml_features(df_prix)
        assert df.isna().sum().sum() == 0

    def test_create_ml_features_ne_modifie_pas_original(self, engineer, df_prix):
        """Vérifie que le DataFrame original n'est pas modifié."""
        df_original = df_prix.copy()
        engineer.create_ml_features(df_prix)
        pd.testing.assert_frame_equal(df_prix, df_original)