"""
Tests unitaires pour PairsSelector.
Pattern AAA (Arrange-Act-Assert).
"""

import pytest
import numpy as np
import pandas as pd
from backend.app.core.pairs_selector import PairsSelector


# ========== TESTS ==========

class TestPairsSelector:

    # ===== FIXTURES =====

    @pytest.fixture
    def selector(self):
        """Fixture : PairsSelector avec seuils par défaut."""
        return PairsSelector()

    @pytest.fixture
    def prix_correles(self):
        """
        Fixture : DataFrame 3 colonnes.
        AAPL et MSFT fortement corrélées, RAND indépendante.
        """
        np.random.seed(42)
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        base = np.cumsum(np.random.randn(100))
        msft = base + np.random.randn(100) * 0.5
        rand = np.cumsum(np.random.randn(100))

        return pd.DataFrame({
            'AAPL': base,
            'MSFT': msft,
            'RAND': rand
        }, index=dates)

    @pytest.fixture
    def series_cointegrees(self):
        """
        Fixture : tuple (series_a, series_b) construites pour être cointégrées.
        """
        np.random.seed(42)
        series_a = pd.Series(np.cumsum(np.random.randn(500)))
        series_b = pd.Series(series_a + np.random.randn(500) * 0.5)
        return (series_a, series_b)

    @pytest.fixture
    def series_non_cointegrees(self):
        """
        Fixture : tuple (series_a, series_b) deux marches aléatoires indépendantes.
        """
        np.random.seed(42)
        series_a = pd.Series(np.cumsum(np.random.randn(500)))
        series_b = pd.Series(np.cumsum(np.random.randn(500)))
        return (series_a, series_b)

    # ===== TESTS calculate_correlation() =====

    def test_correlation_retourne_dataframe(self, selector, prix_correles):
        """calculate_correlation() doit retourner un DataFrame."""
        # ACT
        df = selector.calculate_correlation(prix_correles)
        # ASSERT
        assert isinstance(df, pd.DataFrame)

    def test_correlation_matrice_carree(self, selector, prix_correles):
        """La matrice de corrélation doit être carrée NxN."""
        # ACT
        matrice = selector.calculate_correlation(prix_correles)
        # ASSERT
        assert matrice.shape[0] == matrice.shape[1] == len(prix_correles.columns)

    def test_correlation_diagonale_egale_un(self, selector, prix_correles):
        """Chaque actif est corrélé à 1.0 avec lui-même."""
        # ACT
        matrice = selector.calculate_correlation(prix_correles)
        # ASSERT
        for valeur in np.diag(matrice.values):
            assert valeur == pytest.approx(1.0)

    def test_correlation_forte_detectee(self, selector, prix_correles):
        """AAPL et MSFT (séries identiques + bruit) doivent avoir corr >= 0.7."""
        # ACT
        matrice = selector.calculate_correlation(prix_correles)
        # ASSERT
        assert matrice.loc['AAPL', 'MSFT'] >= 0.7

    # ===== TESTS test_cointegration() =====

    def test_cointegration_types_corrects(self, selector, series_cointegrees):
        """Le tuple doit contenir (bool, float)."""
        # ARRANGE
        series_a, series_b = series_cointegrees
        # ACT
        resultat = selector.test_cointegration(series_a, series_b)
        # ASSERT
        assert len(resultat) == 2
        assert isinstance(resultat[0], bool)
        assert isinstance(resultat[1], float)

    def test_cointegration_series_cointegrees(self, selector, series_cointegrees):
        """Des séries cointégrées doivent retourner est_cointegree=True."""
        # ARRANGE
        series_a, series_b = series_cointegrees
        # ACT
        est_cointegree, _ = selector.test_cointegration(series_a, series_b)
        # ASSERT
        assert est_cointegree is True

    def test_cointegration_series_non_cointegrees(self, selector, series_non_cointegrees):
        """Deux marches aléatoires indépendantes doivent retourner est_cointegree=False."""
        # ARRANGE
        series_a, series_b = series_non_cointegrees
        # ACT
        est_cointegree, _ = selector.test_cointegration(series_a, series_b)
        # ASSERT
        assert est_cointegree is False

    def test_cointegration_pvalue_entre_0_et_1(self, selector, series_cointegrees):
        """La p-value retournée doit toujours être comprise entre 0 et 1."""
        # ARRANGE
        series_a, series_b = series_cointegrees
        # ACT
        _, p_valeur = selector.test_cointegration(series_a, series_b)
        # ASSERT
        assert 0.0 <= p_valeur <= 1.0

    # ===== TESTS find_all_pairs() =====

    def test_find_all_pairs_nombre_correct(self, selector):
        """4 tickers => C(4,2) = 6 paires."""
        # ARRANGE
        tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA']
        # ACT
        paires = selector.find_all_pairs(tickers)
        # ASSERT
        assert len(paires) == 6

    def test_find_all_pairs_retourne_liste_de_tuples(self, selector):
        """Chaque élément retourné doit être un tuple."""
        # ARRANGE
        tickers = ['AAPL', 'MSFT', 'GOOGL']
        # ACT
        paires = selector.find_all_pairs(tickers)
        # ASSERT
        assert all(isinstance(p, tuple) for p in paires)

    def test_find_all_pairs_deux_tickers(self, selector):
        """Cas minimal : 2 tickers => 1 seule paire."""
        # ARRANGE
        tickers = ['AAPL', 'MSFT']
        # ACT
        paires = selector.find_all_pairs(tickers)
        # ASSERT
        assert len(paires) == 1

    def test_find_all_pairs_un_ticker(self, selector):
        """Cas limite : 1 ticker => liste vide."""
        # ARRANGE
        tickers = ['AAPL']
        # ACT
        paires = selector.find_all_pairs(tickers)
        # ASSERT
        assert paires == []

    # ===== TESTS filter_valid_pairs() =====

    def test_filter_paire_valide_acceptee(self, selector):
        """corr=0.85, pvalue=0.02 : doit être acceptée."""
        # ARRANGE
        paires = [('AAPL', 'MSFT', 0.85, 0.02)]
        # ACT
        resultat = selector.filter_valid_pairs(paires)
        # ASSERT
        assert len(resultat) == 1

    def test_filter_correlation_insuffisante(self, selector):
        """corr=0.65 < 0.7 : rejetée même si pvalue est bonne."""
        # ARRANGE
        paires = [('AAPL', 'MSFT', 0.65, 0.02)]
        # ACT
        resultat = selector.filter_valid_pairs(paires)
        # ASSERT
        assert len(resultat) == 0

    def test_filter_pvalue_trop_haute(self, selector):
        """pvalue=0.15 > 0.05 : rejetée même si corrélation est bonne."""
        # ARRANGE
        paires = [('AAPL', 'MSFT', 0.90, 0.15)]
        # ACT
        resultat = selector.filter_valid_pairs(paires)
        # ASSERT
        assert len(resultat) == 0

    def test_filter_liste_vide(self, selector):
        """Une liste vide en entrée doit retourner une liste vide."""
        # ARRANGE
        paires = []
        # ACT
        resultat = selector.filter_valid_pairs(paires)
        # ASSERT
        assert resultat == []

    def test_filter_seuils_personnalises(self):
        """Un selector avec seuils custom doit respecter ses propres seuils."""
        # ARRANGE
        selector_custom = PairsSelector(correlation_threshold=0.9, pvalue_threshold=0.01)
        paires = [
            ('AAPL', 'MSFT', 0.95, 0.005),  # acceptée
            ('AAPL', 'GOOGL', 0.85, 0.005), # corr < 0.9 => rejetée
        ]
        # ACT
        resultat = selector_custom.filter_valid_pairs(paires)
        # ASSERT
        assert len(resultat) == 1
        assert resultat[0][0] == 'AAPL' and resultat[0][1] == 'MSFT'