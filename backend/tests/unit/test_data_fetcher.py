"""
Tests unitaires pour DataFetcher.
Pattern AAA (Arrange-Act-Assert).
"""

import pytest
import pandas as pd
from pathlib import Path
from backend.app.core.data_fetcher import DataFetcher
from backend.app.core.data_source import DataSource

# ========== DATA SOURCE FICTIVE ==========

class FakeDataSource(DataSource):
    """
    Fausse source de données pour les tests.
    Retourne toujours le même DataFrame synthétique,
    sans aucun appel réseau.
    """
    def __init__(self):
        self.nb_appels = 0  # Pour vérifier combien de fois on a appelé telecharger()

    def telecharger(self, ticker, start_date, end_date):
        self.nb_appels += 1
        dates = pd.date_range(start_date, periods=5, freq='D')
        return pd.DataFrame({
            'Close': [100.0, 101.0, 102.0, 103.0, 104.0],
            'Open':  [99.0,  100.0, 101.0, 102.0, 103.0],
        }, index=dates)

# ========== TESTS ==========

class TestDataFetcher:

    @pytest.fixture
    def source(self):
        """Fixture : fausse source de données."""
        return FakeDataSource()

    @pytest.fixture
    def fetcher(self, source, tmp_path):
        """
        Fixture : DataFetcher avec source fake et cache temporaire.
        tmp_path est un dossier temporaire fourni par pytest (supprimé après le test).
        """
        return DataFetcher(
            source=source,
            cache_dir=tmp_path
        )

    # ===== TESTS get_cached_data =====

    def test_telecharge_si_cache_absent(self, fetcher, source):
        """Si le cache n'existe pas, telecharger() doit être appelé une fois."""
        # ACT 
        df = fetcher.get_cached_data('AAPL', '2024-01-01', '2024-01-31')
        # ASSERT 
        assert source.nb_appels == 1
        assert isinstance(df, pd.DataFrame)


    def test_lit_cache_si_present(self, fetcher, source, tmp_path):
        """Si le cache existe, telecharger() ne doit PAS être appelé."""
        # ARRANGE 
        df1 = fetcher.get_cached_data('AAPL', '2024-01-01', '2024-01-31')
        # ACT 
        df2 = fetcher.get_cached_data('AAPL', '2024-01-01', '2024-01-31')
        # ASSERT 
        assert source.nb_appels == 1

    def test_donnees_identiques_cache(self, fetcher, source, tmp_path):
        """Les données lues depuis le cache doivent être identiques à l'original."""
        # ARRANGE 
        df1 = fetcher.get_cached_data('AAPL', '2024-01-01', '2024-01-31')
        # ACT 
        df2 = fetcher.get_cached_data('AAPL', '2024-01-01', '2024-01-31')
        # ASSERT 
        pd.testing.assert_frame_equal(df1, df2, check_freq=False)

    # ===== TESTS download_pair =====

    def test_download_pair_retourne_dataframe(self, fetcher):
        """download_pair doit retourner un DataFrame."""
        # ACT
        df = fetcher.download_pair('AAPL', 'MSFT', '2024-01-01', '2024-01-31')
        # ASSERT
        assert isinstance(df, pd.DataFrame)

    def test_download_pair_colonnes_suffixees(self, fetcher):
        """Les colonnes doivent être suffixées avec les noms des tickers."""
        # ARRANGE
        ticker_a, ticker_b = 'AAPL', 'MSFT'
        # ACT
        df = fetcher.download_pair(ticker_a, ticker_b, '2024-01-01', '2024-01-31')
        # ASSERT 
        assert 'Close_AAPL' in df.columns and 'Close_MSFT' in df.columns

    def test_download_pair_dates_communes(self, fetcher):
        """download_pair doit aligner les deux séries sur les dates communes."""
        # ACT
        df = fetcher.download_pair('AAPL', 'MSFT', '2024-01-01', '2024-01-31')
        # ASSERT 
        assert len(df) == 5