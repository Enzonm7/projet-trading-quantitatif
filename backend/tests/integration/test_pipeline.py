"""
Tests unitaires pour TradingPipeline.
Pattern AAA (Arrange-Act-Assert).
"""

import pytest
import numpy as np
import pandas as pd
from unittest.mock import MagicMock
from backend.app.pipeline import TradingPipeline
from backend.app.core.strategies import Strategy


# ========== FAKE STRATEGY ==========

class FakeStrategy(Strategy):
    """Fausse stratégie pour les tests, sans calcul réel."""
    def generer_signaux(self, prix_a: pd.Series, prix_b: pd.Series) -> pd.DataFrame:
        n = len(prix_a)
        positions = [0] * n
        positions[10:20] = [1] * 10
        positions[30:40] = [-1] * 10
        return pd.DataFrame({
            'zscore':   np.random.randn(n),
            'signal':   [0] * n,
            'position': positions,
            'spread':   np.random.randn(n),
            'ratio':    [1.2] * n
        }, index=prix_a.index)


# ========== TESTS ==========

class TestTradingPipeline:

    # ===== FIXTURES =====

    @pytest.fixture
    def donnees_paire(self):
        """Fixture : DataFrame simulant download_pair()."""
        np.random.seed(42)
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        prix_a = 100 + np.cumsum(np.random.randn(100))
        prix_b = 100 + np.cumsum(np.random.randn(100))
        return pd.DataFrame({
            'Close_AAPL': prix_a,
            'Close_MSFT': prix_b,
        }, index=dates)

    @pytest.fixture
    def pipeline(self, donnees_paire):
        """
        Fixture : TradingPipeline avec tous les composants mockés.
        Zéro appel réseau, zéro fichier.
        """
        from backend.app.core.data_fetcher import DataFetcher
        from backend.app.core.pairs_selector import PairsSelector
        from backend.app.core.backtester import Backtester
        from backend.app.core.risk_manager import RiskManager

        # Mock fetcher
        fetcher = MagicMock(spec=DataFetcher)
        fetcher.download_pair.return_value = donnees_paire

        # Vrais composants avec FakeStrategy
        selector = PairsSelector()
        backtester = Backtester(strategy=FakeStrategy(), capital_initial=10000.0)
        risk_manager = RiskManager()

        return TradingPipeline(
            fetcher=fetcher,
            selector=selector,
            backtester=backtester,
            risk_manager=risk_manager
        )

    # ===== TESTS executer_backtest() =====

    def test_executer_backtest_retourne_dict(self, pipeline):
        """executer_backtest() doit retourner un dictionnaire."""
        # ACT
        resultats = pipeline.executer_backtest('AAPL', 'MSFT', '2024-01-01', '2024-06-30')
        # ASSERT
        assert isinstance(resultats, dict)

    def test_executer_backtest_cles_presentes(self, pipeline):
        """Le dictionnaire doit contenir toutes les clés attendues."""
        # ARRANGE
        cles_attendues = [
            'ticker_a', 'ticker_b', 'donnees_paire', 'est_cointegree',
            'p_valeur', 'ratio_couverture', 'spread', 'zscore',
            'df_signaux', 'df_trades', 'df_risque', 'metriques', 'metriques_risque'
        ]
        # ACT
        resultats = pipeline.executer_backtest('AAPL', 'MSFT', '2024-01-01', '2024-06-30')
        # ASSERT
        for cle in cles_attendues:
            assert cle in resultats

    def test_executer_backtest_tickers_corrects(self, pipeline):
        """Les tickers dans le résultat doivent correspondre aux arguments."""
        # ACT
        resultats = pipeline.executer_backtest('AAPL', 'MSFT', '2024-01-01', '2024-06-30')
        # ASSERT
        assert resultats['ticker_a'] == 'AAPL'
        assert resultats['ticker_b'] == 'MSFT'

    def test_executer_backtest_avec_risk_management(self, pipeline):
        """Avec appliquer_risk_management=True, df_risque et metriques_risque ne sont pas None."""
        # ACT
        resultats = pipeline.executer_backtest(
            'AAPL', 'MSFT', '2024-01-01', '2024-06-30',
            appliquer_risk_management=True
        )
        # ASSERT
        assert resultats['df_risque'] is not None
        assert resultats['metriques_risque'] is not None

    def test_executer_backtest_sans_risk_management(self, pipeline):
        """Avec appliquer_risk_management=False, df_risque et metriques_risque sont None."""
        # ACT
        resultats = pipeline.executer_backtest(
            'AAPL', 'MSFT', '2024-01-01', '2024-06-30',
            appliquer_risk_management=False
        )
        # ASSERT
        assert resultats['df_risque'] is None
        assert resultats['metriques_risque'] is None

    def test_executer_backtest_metriques_sont_dict(self, pipeline):
        """Les métriques retournées doivent être un dictionnaire."""
        # ACT
        resultats = pipeline.executer_backtest('AAPL', 'MSFT', '2024-01-01', '2024-06-30')
        # ASSERT
        assert isinstance(resultats['metriques'], dict)

    # ===== TESTS analyser_univers() =====

    def test_analyser_univers_retourne_liste(self, pipeline):
        """analyser_univers() doit retourner une liste."""
        # ARRANGE
        tickers = ['AAPL', 'MSFT', 'GOOGL']
        # ACT
        resultats = pipeline.analyser_univers(tickers, '2024-01-01', '2024-06-30')
        # ASSERT
        assert isinstance(resultats, list)

    def test_analyser_univers_nombre_paires_correct(self, pipeline, donnees_paire):
        """3 tickers => C(3,2) = 3 paires analysées."""
        # ARRANGE
        tickers = ['AAPL', 'MSFT', 'GOOGL']
        dates = donnees_paire.index
        np.random.seed(42)

        def fake_download_pair(ticker_a, ticker_b, *args, **kwargs):
            return pd.DataFrame({
                f'Close_{ticker_a}': 100 + np.cumsum(np.random.randn(100)),
                f'Close_{ticker_b}': 100 + np.cumsum(np.random.randn(100)),
            }, index=dates)

        pipeline.fetcher.download_pair.side_effect = fake_download_pair
        # ACT
        resultats = pipeline.analyser_univers(tickers, '2024-01-01', '2024-06-30')
        # ASSERT
        assert len(resultats) == 3

    def test_analyser_univers_cles_presentes(self, pipeline):
        """Chaque résumé doit contenir les clés attendues."""
        # ARRANGE
        tickers = ['AAPL', 'MSFT']
        cles_attendues = ['paire', 'est_cointegree', 'p_valeur', 'sharpe_ratio', 'rendement_total', 'max_drawdown']
        # ACT
        resultats = pipeline.analyser_univers(tickers, '2024-01-01', '2024-06-30')
        # ASSERT
        for cle in cles_attendues:
            assert cle in resultats[0]

    def test_analyser_univers_trie_par_sharpe(self, pipeline):
        """Les résultats doivent être triés par Sharpe Ratio décroissant."""
        # ARRANGE
        tickers = ['AAPL', 'MSFT', 'GOOGL']
        # ACT
        resultats = pipeline.analyser_univers(tickers, '2024-01-01', '2024-06-30')
        # ASSERT
        sharpes = [r['sharpe_ratio'] for r in resultats]
        assert sharpes == sorted(sharpes, reverse=True)

    # ===== TESTS sauvegarder_resultats() =====

    def test_sauvegarder_resultats_cree_fichiers(self, pipeline, tmp_path):
        """sauvegarder_resultats() doit créer les 3 fichiers CSV attendus."""
        # ARRANGE
        resultats = pipeline.executer_backtest('AAPL', 'MSFT', '2024-01-01', '2024-06-30')
        # ACT
        pipeline.sauvegarder_resultats(resultats, dossier=str(tmp_path))
        # ASSERT
        assert (tmp_path / "AAPL_MSFT_signaux.csv").exists()
        assert (tmp_path / "AAPL_MSFT_trades.csv").exists()
        assert (tmp_path / "AAPL_MSFT_metriques.csv").exists()

    def test_sauvegarder_resultats_cree_dossier(self, pipeline, tmp_path):
        """sauvegarder_resultats() doit créer le dossier s'il n'existe pas."""
        # ARRANGE
        resultats = pipeline.executer_backtest('AAPL', 'MSFT', '2024-01-01', '2024-06-30')
        dossier = str(tmp_path / "nouveau_dossier")
        # ACT
        pipeline.sauvegarder_resultats(resultats, dossier=dossier)
        # ASSERT
        assert (tmp_path / "nouveau_dossier").exists()