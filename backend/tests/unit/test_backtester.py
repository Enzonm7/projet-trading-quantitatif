"""
Tests unitaires pour Backtester.
Pattern AAA (Arrange-Act-Assert).
"""

import pytest
import numpy as np
import pandas as pd
from backend.app.core.backtester import Backtester
from backend.app.core.strategies import Strategy


# ========== FAKE STRATEGY ==========

class FakeStrategy(Strategy):
    """
    Fausse stratégie pour les tests.
    Retourne un df_signaux synthétique sans calcul réel.
    """
    def generer_signaux(self, prix_a: pd.Series, prix_b: pd.Series) -> pd.DataFrame:
        n = len(prix_a)
        index = prix_a.index
        signaux = [0] * n
        positions = [0] * n

        signaux[10] = 1
        positions[10:20] = [1] * 10
        signaux[30] = -1
        positions[30:40] = [-1] * 10

        return pd.DataFrame({
            'zscore': np.random.randn(n),
            'signal': signaux,
            'position': positions,
            'spread': np.random.randn(n),
            'ratio': [1.2] * n
        }, index=index)


# ========== TESTS ==========

class TestBacktester:

    # ===== FIXTURES =====

    @pytest.fixture
    def strategy(self):
        """Fixture : fausse stratégie sans calcul réel."""
        return FakeStrategy()

    @pytest.fixture
    def backtester(self, strategy):
        """Fixture : Backtester avec FakeStrategy et capital par défaut."""
        return Backtester(strategy=strategy, capital_initial=10000.0)

    @pytest.fixture
    def prix_synthetiques(self):
        """Fixture : deux séries de prix synthétiques alignées."""
        np.random.seed(42)
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        prix_a = pd.Series(100 + np.cumsum(np.random.randn(100)), index=dates)
        prix_b = pd.Series(100 + np.cumsum(np.random.randn(100)), index=dates)
        return prix_a, prix_b

    @pytest.fixture
    def df_signaux(self, prix_synthetiques):
        """Fixture : df_signaux synthétique prêt pour simuler_trades."""
        prix_a, prix_b = prix_synthetiques
        strategy = FakeStrategy()
        return strategy.generer_signaux(prix_a, prix_b)

    @pytest.fixture
    def df_trades(self, backtester, df_signaux, prix_synthetiques):
        """Fixture : df_trades prêt pour calculer_metriques."""
        prix_a, prix_b = prix_synthetiques
        ratio = df_signaux['ratio'].iloc[0]
        return backtester.simuler_trades(df_signaux, prix_a, prix_b, ratio)

    # ===== TESTS simuler_trades() =====

    def test_simuler_trades_retourne_dataframe(self, backtester, df_signaux, prix_synthetiques):
        """simuler_trades() doit retourner un DataFrame."""
        # ARRANGE
        prix_a, prix_b = prix_synthetiques
        ratio = df_signaux['ratio'].iloc[0]
        # ACT
        df_trades = backtester.simuler_trades(df_signaux, prix_a, prix_b, ratio)
        # ASSERT
        assert isinstance(df_trades, pd.DataFrame)

    def test_simuler_trades_colonnes_presentes(self, backtester, df_signaux, prix_synthetiques):
        """Le DataFrame retourné doit contenir les colonnes attendues."""
        # ARRANGE
        prix_a, prix_b = prix_synthetiques
        ratio = df_signaux['ratio'].iloc[0]
        colonnes_attendues = ['position', 'pnl_quotidien', 'pnl_cumule', 'capital']
        # ACT
        df_trades = backtester.simuler_trades(df_signaux, prix_a, prix_b, ratio)
        # ASSERT
        for colonne in colonnes_attendues:
            assert colonne in df_trades.columns

    def test_simuler_trades_capital_initial_correct(self, backtester, df_signaux, prix_synthetiques):
        """La première valeur de capital doit être proche du capital initial."""
        # ARRANGE
        prix_a, prix_b = prix_synthetiques
        ratio = df_signaux['ratio'].iloc[0]
        # ACT
        df_trades = backtester.simuler_trades(df_signaux, prix_a, prix_b, ratio)
        # ASSERT
        assert df_trades['capital'].iloc[0] == pytest.approx(10000.0, rel=0.01)

    def test_simuler_trades_meme_longueur(self, backtester, df_signaux, prix_synthetiques):
        """Le DataFrame retourné doit avoir le même nombre de lignes que df_signaux."""
        # ARRANGE
        prix_a, prix_b = prix_synthetiques
        ratio = df_signaux['ratio'].iloc[0]
        # ACT
        df_trades = backtester.simuler_trades(df_signaux, prix_a, prix_b, ratio)
        # ASSERT
        assert len(df_trades) == len(df_signaux)

    # ===== TESTS calculer_metriques() =====

    def test_calculer_metriques_retourne_dict(self, backtester, df_trades):
        """calculer_metriques() doit retourner un dictionnaire."""
        # ACT
        metriques = backtester.calculer_metriques(df_trades)
        # ASSERT
        assert isinstance(metriques, dict)

    def test_calculer_metriques_cles_presentes(self, backtester, df_trades):
        """Le dictionnaire doit contenir les 5 clés attendues."""
        # ARRANGE
        cles_attendues = ['rendement_total', 'sharpe_ratio', 'max_drawdown', 'win_rate', 'nombre_trades']
        # ACT
        metriques = backtester.calculer_metriques(df_trades)
        # ASSERT
        for cle in cles_attendues:
            assert cle in metriques

    def test_calculer_metriques_types_corrects(self, backtester, df_trades):
        """rendement_total, sharpe_ratio, max_drawdown, win_rate doivent être des floats."""
        # ACT
        metriques = backtester.calculer_metriques(df_trades)
        # ASSERT
        assert isinstance(metriques['rendement_total'], float)
        assert isinstance(metriques['sharpe_ratio'], float)
        assert isinstance(metriques['max_drawdown'], float)
        assert isinstance(metriques['win_rate'], float)

    def test_calculer_metriques_win_rate_entre_0_et_100(self, backtester, df_trades):
        """Le win_rate doit toujours être compris entre 0 et 100."""
        # ACT
        metriques = backtester.calculer_metriques(df_trades)
        # ASSERT
        assert 0.0 <= metriques['win_rate'] <= 100.0

    def test_calculer_metriques_max_drawdown_negatif(self, backtester, df_trades):
        """Le max_drawdown doit être <= 0 (c'est une perte)."""
        # ACT
        metriques = backtester.calculer_metriques(df_trades)
        # ASSERT
        assert metriques['max_drawdown'] <= 0.0