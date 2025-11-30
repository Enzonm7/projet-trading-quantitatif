"""Module PairsSelector pour l'identification de paires corrélées et cointégrées."""

import numpy as np
import pandas as pd
from scipy import stats
from typing import List, Tuple
from itertools import combinations
from statsmodels.tsa.stattools import adfuller


class PairsSelector:
    """
    Classe responsable de l'identification des paires d'actions
    corrélées et cointégrées pour le pairs trading.
    """

    def __init__(self, correlation_threshold: float = 0.7, pvalue_threshold: float = 0.05):
        """
        Initialise le PairsSelector.
        
        Args:
            correlation_threshold: Seuil minimum de corrélation (défaut: 0.7)
            pvalue_threshold: Seuil maximum de p-value pour cointégration (défaut: 0.05)
        """
        self.correlation_threshold = correlation_threshold
        self.pvalue_threshold = pvalue_threshold

    
    def calculate_correlation(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calcule la matrice de corrélation entre toutes les colonnes.

        Args:
            data: DataFrame avec plusieurs colonnes de prix (une par ticker)

        Returns: 
            DataFrame: Matrice de corrélation NxN
        """
        correlation = data.corr()
        return correlation
    

    def test_cointegration(self, series_a: pd.Series, series_b: pd.Series) -> Tuple[bool, float]:
        """
        Teste la cointégration entre deux séries temporelles.
        
        Args:
            series_a: Série de prix du premier ticker
            series_b: Série de prix du second ticker
            
        Returns:
            Tuple (is_cointegrated, p_value):
                - is_cointegrated: True si cointégré, False sinon
                - p_value: Valeur du test ADF
        """
        # Calculer le ratio optimal via régression linéaire
        slope, intercept = stats.linregress(series_b, series_a)[:2]
        # Claculer le spread  
        spread = series_a - slope * series_b - intercept
        # Test ADF sur le spread
        adf_res = adfuller(spread)
        p_value = adf_res[1] # p_value est à l'index 1
        # Vérifier la cointégration
        is_cointegrated =  p_value < self.pvalue_threshold
        # Retourner le tuple 
        return (is_cointegrated, p_value)      
    

    def find_all_pairs(self, tickers: List[str]) -> List[Tuple[str, str]]:
        """
        Génère toutes les combinaisons possibles de paires.
        
        Args:
            tickers: Liste de symboles boursiers
            
        Returns:
            Liste de tuples (ticker_a, ticker_b) représentant toutes les paires
        """
        pairs = combinations(tickers, 2) 
        return list(pairs)
    

    def filter_valid_pairs(self, pairs: List[Tuple[str, str, float, float]]) -> List[Tuple[str, str, float, float]]:
        """
        Filtre les paires selon les seuils de corrélation et cointégration.
        
        Args:
            pairs: Liste de tuples (ticker_a, ticker_b, correlation, p_value)
            
        Returns:
            Liste filtrée des paires valides
        """
        paires_valides = []
        for pair in pairs:
            ticker_a, ticker_b, correlation, p_value = pair
            if correlation >= self.correlation_threshold and p_value < self.pvalue_threshold:
                paires_valides.append(pair)
        return paires_valides    
        
        
