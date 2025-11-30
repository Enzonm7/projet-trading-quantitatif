"""
Module DataFetcher pour le téléchargement et la gestion du cache des données financières.
"""

import pandas as pd
import yfinance as yf
from pathlib import Path
import pickle

class DataFetcher:
    """
    Classe responsable du téléchargement des données OHLCV depuis Yahoo Finance
    et de la gestion du cache local.
    """
    
    def __init__(self, cache_dir: str = "./cache"):
        """
        Initialise le DataFetcher.
        
        Args:
            cache_dir: Chemin du répertoire de cache (défaut: ./cache)
        """
        self.cache_dir = Path(cache_dir)
        # Créer le dossier cache s'il n'existe pas
        self.cache_dir.mkdir(parents=True, exist_ok=True)


    def download_stock(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Télécharge les données OHLCV d'un ticker depuis Yahoo Finance.
    
        Args:
            ticker: Symbole du ticker (ex: 'AAPL', 'MSFT')
            start_date: Date de début au format 'YYYY-MM-DD'
            end_date: Date de fin au format 'YYYY-MM-DD'
            
        Returns:
            DataFrame avec colonnes: Open, High, Low, Close, Volume
            Index: Date
        """
        try: 
            data = yf.download(ticker, start=start_date, end=end_date, progress=False)
            if data.empty:
                raise ValueError(f"Aucune donnée disponible pour {ticker}")
            if data.columns.nlevels > 1:
                data.columns = [col[0] for col in data.columns]
            return data
        except Exception as e:
            raise ValueError(f"Erreur lors du téléchargement de {ticker}: {str(e)}")
        
        
    def download_pair(self, ticker_a: str, ticker_b: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Télécharge les données de deux tickers et les aligne sur les dates communes.
    
        Args:
            ticker_a: Premier ticker (ex: 'AAPL')
            ticker_b: Second ticker (ex: 'MSFT')
            start_date: Date de début au format 'YYYY-MM-DD'
            end_date: Date de fin au format 'YYYY-MM-DD'
            
        Returns:
            DataFrame avec colonnes suffixées par ticker:
            Close_AAPL, Close_MSFT, Open_AAPL, Open_MSFT, etc.
            Index: Date (seulement les dates communes)
        """
        data_a = self.get_cached_data(ticker_a, start_date, end_date)
        data_b = self.get_cached_data(ticker_b, start_date, end_date)

        pair = data_a.join(data_b, how='inner', lsuffix=f'_{ticker_a}', rsuffix=f'_{ticker_b}')

        return pair
    

    def get_cached_data(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Récupère les données depuis le cache ou télécharge si absent.
    
        Args:
            ticker: Symbole du ticker
            start_date: Date de début au format 'YYYY-MM-DD'
            end_date: Date de fin au format 'YYYY-MM-DD'
            
        Returns:
            DataFrame avec les données OHLCV
        """
        cache_filename = f"{ticker}_{start_date}_{end_date}.pkl"
        cache_path = self.cache_dir / cache_filename

        if cache_path.exists():
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)
        else:
            data = self.download_stock(ticker, start_date, end_date)
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
        return data