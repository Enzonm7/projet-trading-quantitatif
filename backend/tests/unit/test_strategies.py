"""
Tests unitaires pour le module strategies.
Pattern AAA (Arrange-Act-Assert) pour tous les tests.
"""

import pytest
import pandas as pd
import numpy as np
from backend.app.core.strategies import Strategy, ZScoreReversionStrategy


class TestZScoreReversionStrategy:
    """Tests de la stratégie ZScoreReversionStrategy."""
    
    # ==================== FIXTURES LOCALES ====================
    
    @pytest.fixture
    def strategy(self):
        """Fixture : Instance de stratégie avec paramètres par défaut."""
        return ZScoreReversionStrategy(
            fenetre=20, 
            seuil_entree=2.0, 
            seuil_sortie=0.5
        )
    
    @pytest.fixture
    def prix_simples(self):
        """Fixture : Données de prix simples avec seed fixe."""
        np.random.seed(42)  # Reproductibilité
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        prix_a = pd.Series(np.random.randn(100).cumsum() + 100, index=dates)
        prix_b = pd.Series(np.random.randn(100).cumsum() + 100, index=dates)
        return prix_a, prix_b
    
    
    # ==================== TESTS D'INITIALISATION ====================
    
    def test_strategy_herite_de_strategy_abc(self, strategy):
        """Vérifie que ZScoreReversionStrategy hérite bien de Strategy."""
        
        # ASSERT
        assert isinstance(strategy, Strategy)
    
    
    def test_initialisation_parametres_defaut(self):
        """Vérifie que les paramètres par défaut sont correctement initialisés."""
        
        # ARRANGE & ACT
        strategy = ZScoreReversionStrategy()
        
        # ASSERT
        assert strategy.fenetre == 20
        assert strategy.seuil_entree == 2.0
        assert strategy.seuil_sortie == 0.5
    
    
    def test_initialisation_parametres_personnalises(self):
        """Vérifie que les paramètres personnalisés sont bien stockés."""
        
        # ARRANGE & ACT
        strategy = ZScoreReversionStrategy(
            fenetre=30, 
            seuil_entree=2.5, 
            seuil_sortie=0.3
        )
        
        # ASSERT
        assert strategy.fenetre == 30
        assert strategy.seuil_entree == 2.5
        assert strategy.seuil_sortie == 0.3
    
    
    # ==================== TESTS DE generer_signaux() ====================
    
    def test_generer_signaux_retourne_dataframe(self, strategy, prix_simples):
        """Vérifie que generer_signaux() retourne un DataFrame."""
        
        # ARRANGE
        prix_a, prix_b = prix_simples
        
        # ACT
        df = strategy.generer_signaux(prix_a, prix_b)
        
        # ASSERT
        assert isinstance(df, pd.DataFrame)
    
    
    def test_generer_signaux_colonnes_requises(self, strategy, prix_simples):
        """Vérifie que le DataFrame contient toutes les colonnes requises."""
        
        # ARRANGE
        prix_a, prix_b = prix_simples
        colonnes_requises = ['zscore', 'signal', 'position', 'spread', 'ratio']
        
        # ACT
        df = strategy.generer_signaux(prix_a, prix_b)
        
        # ASSERT
        for col in colonnes_requises:
            assert col in df.columns, f"Colonne manquante: {col}"
    
    
    def test_generer_signaux_meme_longueur(self, strategy, prix_simples):
        """Vérifie que le DataFrame a la même longueur que les prix d'entrée."""
        
        # ARRANGE
        prix_a, prix_b = prix_simples
        
        # ACT
        df = strategy.generer_signaux(prix_a, prix_b)
        
        # ASSERT
        assert len(df) == len(prix_a)
        assert len(df) == len(prix_b)
    
    
    # ==================== TESTS DE LOGIQUE MÉTIER ====================
    
    def test_signaux_valeurs_valides(self, strategy, prix_simples):
        """Vérifie que les signaux sont uniquement -1, 0 ou 1."""
        
        # ARRANGE
        prix_a, prix_b = prix_simples
        
        # ACT
        df = strategy.generer_signaux(prix_a, prix_b)
        
        # ASSERT
        signaux_uniques = df['signal'].unique()
        for signal in signaux_uniques:
            assert signal in [-1, 0, 1], f"Signal invalide: {signal}"
    
    
    def test_positions_valeurs_valides(self, strategy, prix_simples):
        """Vérifie que les positions sont uniquement -1, 0 ou 1."""
        
        # ARRANGE
        prix_a, prix_b = prix_simples
        
        # ACT
        df = strategy.generer_signaux(prix_a, prix_b)
        
        # ASSERT
        positions_uniques = df['position'].unique()
        for position in positions_uniques:
            assert position in [-1, 0, 1], f"Position invalide: {position}"
    
    
    def test_ratio_est_constant(self, strategy, prix_simples):
        """Vérifie que le ratio de couverture est constant sur toute la série."""
        
        # ARRANGE
        prix_a, prix_b = prix_simples
        
        # ACT
        df = strategy.generer_signaux(prix_a, prix_b)
        
        # ASSERT
        assert df['ratio'].nunique() == 1, "Le ratio devrait être constant"
    
    
    # ==================== TESTS DE CALCULS MATHÉMATIQUES ====================
    
    def test_zscore_contient_nan_debut(self, strategy, prix_simples):
        """Vérifie que le z-score contient des NaN au début (warmup de la fenêtre glissante)."""
        
        # ARRANGE
        prix_a, prix_b = prix_simples
        
        # ACT
        df = strategy.generer_signaux(prix_a, prix_b)
        
        # ASSERT
        # Les premières valeurs (fenetre) devraient être NaN
        nb_nan = df['zscore'].isna().sum()
        assert nb_nan >= strategy.fenetre - 1, f"Attendu au moins {strategy.fenetre-1} NaN, trouvé {nb_nan}"
    
    
    def test_spread_calcule_correctement(self, strategy, prix_simples):
        """Vérifie que le spread est bien calculé (log(Prix_A) - ratio * log(Prix_B))."""
        
        # ARRANGE
        prix_a, prix_b = prix_simples
        
        # ACT
        df = strategy.generer_signaux(prix_a, prix_b)
        
        # ASSERT
        # Vérifier manuellement le calcul sur la dernière ligne (pas de NaN)
        ratio = df['ratio'].iloc[-1]
        spread_attendu = np.log( prix_a).iloc[-1] - ratio * np.log(prix_b).iloc[-1]
        spread_obtenu = df['spread'].iloc[-1]
        
        assert abs(spread_attendu - spread_obtenu) < 0.01, \
            f"Spread incorrect: attendu {spread_attendu:.2f}, obtenu {spread_obtenu:.2f}"
    
    
    # ==================== TESTS DES EDGE CASES ====================
    
    def test_series_trop_courtes(self, strategy):
        """Vérifie le comportement avec des séries plus courtes que la fenêtre."""
        
        # ARRANGE
        # Créer des séries de 15 points (< fenetre=20)
        dates = pd.date_range('2023-01-01', periods=15, freq='D')
        prix_a = pd.Series(range(100, 115), index=dates)
        prix_b = pd.Series(range(100, 115), index=dates)
        
        # ACT
        df = strategy.generer_signaux(prix_a, prix_b)
        
        # ASSERT
        # Le DataFrame devrait être retourné mais avec beaucoup de NaN
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 15
        # La plupart des z-scores seront NaN
        assert df['zscore'].isna().sum() >= 10