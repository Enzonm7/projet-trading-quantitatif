"""
Tests unitaires pour RiskManager.
Pattern AAA (Arrange-Act-Assert).
"""

import pytest
import numpy as np
import pandas as pd
from backend.app.core.risk_manager import RiskManager


# ========== TESTS ==========

class TestRiskManager:

    # ===== FIXTURES =====

    @pytest.fixture
    def risk_manager(self):
        """Fixture : RiskManager avec paramètres par défaut."""
        return RiskManager(max_position_size=0.1, stop_loss_pct=0.02, max_leverage=1.0)

    @pytest.fixture
    def df_trades(self):
        """Fixture : DataFrame de trades synthétique pour les tests."""
        np.random.seed(42)
        n = 100
        dates = pd.date_range('2024-01-01', periods=n, freq='D')
        pnl_quotidien = np.random.randn(n) * 50
        pnl_cumule = np.cumsum(pnl_quotidien)
        return pd.DataFrame({
            'position': [0]*10 + [1]*20 + [0]*10 + [-1]*20 + [0]*40,
            'pnl_quotidien': pnl_quotidien,
            'pnl_cumule': pnl_cumule,
            'capital': 10000.0 + pnl_cumule,
        }, index=dates)

    @pytest.fixture
    def prix_synthetiques(self):
        """Fixture : deux séries de prix synthétiques alignées."""
        np.random.seed(42)
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        prix_a = pd.Series(100 + np.cumsum(np.random.randn(100)), index=dates)
        prix_b = pd.Series(100 + np.cumsum(np.random.randn(100)), index=dates)
        return prix_a, prix_b

    # ===== TESTS calculer_taille_position() =====

    def test_taille_position_sans_volatilite(self, risk_manager):
        """Sans volatilité, la taille = capital * max_position_size."""
        # ARRANGE
        capital = 10000.0
        # ACT
        taille = risk_manager.calculer_taille_position(capital)
        # ASSERT
        assert taille == pytest.approx(1000.0)

    def test_taille_position_avec_volatilite_reduit_taille(self, risk_manager):
        """Avec volatilité, la taille doit être inférieure à la taille de base."""
        # ARRANGE
        capital = 10000.0
        taille_base = risk_manager.calculer_taille_position(capital)
        # ACT
        taille_avec_vol = risk_manager.calculer_taille_position(capital, volatilite=0.05)
        # ASSERT
        assert taille_avec_vol < taille_base

    def test_taille_position_volatilite_elevee_inferieure_faible(self, risk_manager):
        """Une volatilité élevée produit une taille de position plus petite."""
        # ARRANGE
        capital = 10000.0
        # ACT
        taille_faible = risk_manager.calculer_taille_position(capital, volatilite=0.01)
        taille_elevee = risk_manager.calculer_taille_position(capital, volatilite=0.05)
        # ASSERT
        assert taille_elevee < taille_faible

    def test_taille_position_capital_negatif_leve_erreur(self, risk_manager):
        """Un capital négatif doit lever une ValueError."""
        # ACT & ASSERT
        with pytest.raises(ValueError):
            risk_manager.calculer_taille_position(-1000.0)

    def test_taille_position_capital_zero_leve_erreur(self, risk_manager):
        """Un capital nul doit lever une ValueError."""
        # ACT & ASSERT
        with pytest.raises(ValueError):
            risk_manager.calculer_taille_position(0.0)

    # ===== TESTS verifier_stop_loss() =====

    def test_stop_loss_non_declenche(self, risk_manager):
        """Une perte inférieure au seuil ne déclenche pas le stop-loss."""
        # ARRANGE
        capital_initial = 10000.0
        capital_actuel = 9850.0  # perte de 1.5% < 2%
        # ACT
        stop_declenche, perte_pct = risk_manager.verifier_stop_loss(capital_initial, capital_actuel)
        # ASSERT
        assert stop_declenche is False

    def test_stop_loss_declenche(self, risk_manager):
        """Une perte supérieure au seuil déclenche le stop-loss."""
        # ARRANGE
        capital_initial = 10000.0
        capital_actuel = 9750.0  # perte de 2.5% > 2%
        # ACT
        stop_declenche, perte_pct = risk_manager.verifier_stop_loss(capital_initial, capital_actuel)
        # ASSERT
        assert stop_declenche is True

    def test_stop_loss_retourne_perte_correcte(self, risk_manager):
        """La perte retournée doit être correctement calculée."""
        # ARRANGE
        capital_initial = 10000.0
        capital_actuel = 9000.0  # perte de 10%
        # ACT
        _, perte_pct = risk_manager.verifier_stop_loss(capital_initial, capital_actuel)
        # ASSERT
        assert perte_pct == pytest.approx(0.10)

    def test_stop_loss_retourne_tuple(self, risk_manager):
        """verifier_stop_loss() doit retourner un tuple (bool, float)."""
        # ACT
        resultat = risk_manager.verifier_stop_loss(10000.0, 9900.0)
        # ASSERT
        assert isinstance(resultat, tuple)
        assert len(resultat) == 2
        assert isinstance(resultat[0], bool)
        assert isinstance(resultat[1], float)

    # ===== TESTS verifier_stop_loss_position() =====

    def test_stop_loss_position_long_non_declenche(self, risk_manager):
        """Position LONG avec perte faible : stop-loss non déclenché."""
        # ARRANGE
        prix_entree, prix_actuel = 150.0, 148.0  # perte de ~1.3% < 5%
        # ACT
        stop = risk_manager.verifier_stop_loss_position(prix_entree, prix_actuel, 1)
        # ASSERT
        assert stop is False

    def test_stop_loss_position_long_declenche(self, risk_manager):
        """Position LONG avec perte > 5% : stop-loss déclenché."""
        # ARRANGE
        prix_entree, prix_actuel = 150.0, 142.0  # perte de ~5.3% > 5%
        # ACT
        stop = risk_manager.verifier_stop_loss_position(prix_entree, prix_actuel, 1)
        # ASSERT
        assert stop is True

    def test_stop_loss_position_short_non_declenche(self, risk_manager):
        """Position SHORT avec hausse faible : stop-loss non déclenché."""
        # ARRANGE
        prix_entree, prix_actuel = 150.0, 152.0  # hausse de ~1.3% < 5%
        # ACT
        stop = risk_manager.verifier_stop_loss_position(prix_entree, prix_actuel, -1)
        # ASSERT
        assert stop is False

    def test_stop_loss_position_short_declenche(self, risk_manager):
        """Position SHORT avec hausse > 5% : stop-loss déclenché."""
        # ARRANGE
        prix_entree, prix_actuel = 150.0, 158.0  # hausse de ~5.3% > 5%
        # ACT
        stop = risk_manager.verifier_stop_loss_position(prix_entree, prix_actuel, -1)
        # ASSERT
        assert stop is True

    def test_stop_loss_position_neutre_retourne_false(self, risk_manager):
        """Position neutre (0) : stop-loss toujours False."""
        # ACT
        stop = risk_manager.verifier_stop_loss_position(150.0, 100.0, 0)
        # ASSERT
        assert stop is False

    # ===== TESTS ajuster_leverage() =====

    def test_leverage_sharpe_faible_retourne_un(self, risk_manager):
        """Sharpe < 1 : leverage = 1.0 (pas de leverage)."""
        # ACT
        leverage = risk_manager.ajuster_leverage(0.5, 10000.0)
        # ASSERT
        assert leverage == pytest.approx(1.0)

    def test_leverage_sharpe_eleve_augmente(self):
        """Sharpe > 1 : leverage doit être > 1.0."""
        # ARRANGE
        rm = RiskManager(max_position_size=0.1, stop_loss_pct=0.02, max_leverage=2.0)
        # ACT
        leverage = rm.ajuster_leverage(2.0, 10000.0)
        # ASSERT
        assert leverage > 1.0

    def test_leverage_ne_depasse_pas_maximum(self, risk_manager):
        """Le leverage ne doit jamais dépasser max_leverage."""
        # ACT
        leverage = risk_manager.ajuster_leverage(10.0, 10000.0)
        # ASSERT
        assert leverage <= risk_manager.max_leverage

    # ===== TESTS calculer_metriques_risque() =====

    def test_metriques_risque_retourne_dict(self, risk_manager, df_trades):
        """calculer_metriques_risque() doit retourner un dictionnaire."""
        # ACT
        metriques = risk_manager.calculer_metriques_risque(df_trades, 10000.0)
        # ASSERT
        assert isinstance(metriques, dict)

    def test_metriques_risque_cles_presentes(self, risk_manager, df_trades):
        """Le dictionnaire doit contenir les 5 clés attendues."""
        # ARRANGE
        cles_attendues = ['perte_maximale', 'perte_maximale_pct', 'volatilite_quotidienne', 'var_95', 'ratio_gain_perte']
        # ACT
        metriques = risk_manager.calculer_metriques_risque(df_trades, 10000.0)
        # ASSERT
        for cle in cles_attendues:
            assert cle in metriques

    def test_metriques_risque_perte_maximale_positive(self, risk_manager, df_trades):
        """La perte maximale en euros doit être >= 0."""
        # ACT
        metriques = risk_manager.calculer_metriques_risque(df_trades, 10000.0)
        # ASSERT
        assert metriques['perte_maximale'] >= 0.0

    def test_metriques_risque_volatilite_positive(self, risk_manager, df_trades):
        """La volatilité quotidienne doit être >= 0."""
        # ACT
        metriques = risk_manager.calculer_metriques_risque(df_trades, 10000.0)
        # ASSERT
        assert metriques['volatilite_quotidienne'] >= 0.0