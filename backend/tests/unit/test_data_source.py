"""
Tests unitaires pour DataSource.
Pattern AAA (Arrange-Act-Assert).
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from backend.app.core.data_source import DataSource, YahooFinanceSource, CSVDataSource


# ========== TESTS ==========

class TestDataSource:

    # ===== TESTS YahooFinanceSource =====

    def test_yahoo_retourne_dataframe(self):
        """telecharger() doit retourner un DataFrame."""
        # ARRANGE
        source = YahooFinanceSource()
        df_fake = pd.DataFrame({
            'Close': [150.0, 151.0],
            'Open':  [149.0, 150.0],
        }, index=pd.date_range('2024-01-01', periods=2, freq='D'))

        with patch('yfinance.download', return_value=df_fake):
            # ACT
            result = source.telecharger('AAPL', '2024-01-01', '2024-01-31')
            # ASSERT
            assert isinstance(result, pd.DataFrame)

    def test_yahoo_dataframe_non_vide(self):
        """Le DataFrame retourné ne doit pas être vide."""
        # ARRANGE
        source = YahooFinanceSource()
        df_fake = pd.DataFrame({
            'Close': [150.0, 151.0],
        }, index=pd.date_range('2024-01-01', periods=2, freq='D'))

        with patch('yfinance.download', return_value=df_fake):
            # ACT
            result = source.telecharger('AAPL', '2024-01-01', '2024-01-31')
            # ASSERT
            assert not result.empty

    def test_yahoo_ticker_invalide_leve_erreur(self):
        """Un ticker invalide (données vides) doit lever une ValueError."""
        # ARRANGE
        source = YahooFinanceSource()
        df_vide = pd.DataFrame()

        with patch('yfinance.download', return_value=df_vide):
            # ACT & ASSERT
            with pytest.raises(ValueError):
                source.telecharger('TICKER_INVALIDE', '2024-01-01', '2024-01-31')

    def test_yahoo_aplatit_colonnes_multiniveaux(self):
        """Les colonnes multi-niveaux de yfinance doivent être aplaties."""
        # ARRANGE
        source = YahooFinanceSource()
        index = pd.date_range('2024-01-01', periods=2, freq='D')
        colonnes = pd.MultiIndex.from_tuples([('Close', 'AAPL'), ('Open', 'AAPL')])
        df_multi = pd.DataFrame([[150.0, 149.0], [151.0, 150.0]], index=index, columns=colonnes)

        with patch('yfinance.download', return_value=df_multi):
            # ACT
            result = source.telecharger('AAPL', '2024-01-01', '2024-01-31')
            # ASSERT
            assert result.columns.nlevels == 1

    # ===== TESTS CSVDataSource =====

    def test_csv_retourne_dataframe(self, tmp_path):
        """telecharger() depuis CSV doit retourner un DataFrame."""
        # ARRANGE
        chemin = tmp_path / "test.csv"
        df_fake = pd.DataFrame({
            'Close': [100.0, 101.0],
        }, index=pd.date_range('2024-01-01', periods=2, freq='D'))
        df_fake.index.name = 'Date'
        df_fake.to_csv(chemin)
        source = CSVDataSource(str(chemin))
        # ACT
        result = source.telecharger('AAPL', '2024-01-01', '2024-01-31')
        # ASSERT
        assert isinstance(result, pd.DataFrame)

    def test_csv_donnees_correctes(self, tmp_path):
        """Les données lues depuis le CSV doivent correspondre au fichier original."""
        # ARRANGE
        chemin = tmp_path / "test.csv"
        df_original = pd.DataFrame({
            'Close': [100.0, 101.0, 102.0],
        }, index=pd.date_range('2024-01-01', periods=3, freq='D'))
        df_original.index.name = 'Date'
        df_original.to_csv(chemin)
        source = CSVDataSource(str(chemin))
        # ACT
        result = source.telecharger('AAPL', '2024-01-01', '2024-01-31')
        # ASSERT
        pd.testing.assert_frame_equal(result, df_original, check_freq=False)

    def test_csv_fichier_inexistant_leve_erreur(self, tmp_path):
        """Un chemin CSV inexistant doit lever une FileNotFoundError."""
        # ACT & ASSERT
        with pytest.raises(FileNotFoundError):
            CSVDataSource(str(tmp_path / "inexistant.csv"))

    def test_csv_index_est_datetime(self, tmp_path):
        """L'index du DataFrame lu depuis CSV doit être de type datetime."""
        # ARRANGE
        chemin = tmp_path / "test.csv"
        df_fake = pd.DataFrame({
            'Close': [100.0, 101.0],
        }, index=pd.date_range('2024-01-01', periods=2, freq='D'))
        df_fake.index.name = 'Date'
        df_fake.to_csv(chemin)
        source = CSVDataSource(str(chemin))
        # ACT
        result = source.telecharger('AAPL', '2024-01-01', '2024-01-31')
        # ASSERT
        assert pd.api.types.is_datetime64_any_dtype(result.index)