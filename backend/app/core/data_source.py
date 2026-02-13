"""Module DataSource - Interface abstraite et adapteurs pour les sources de données."""

import pandas as pd
import yfinance as yf
from pathlib import Path
from abc import ABC, abstractmethod


class DataSource(ABC):
    """
    Interface abstraite pour les sources de données financières.
    Toute nouvelle source doit hériter de cette classe 
    et implémenter telecharger().
    """

    @abstractmethod
    def telecharger(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Télécharge les données OHLCV pour un ticker.

        Args:
            ticker: Symbole boursier (ex: 'AAPL')
            start_date: Date de début au format 'YYYY-MM-DD'
            end_date: Date de fin au format 'YYYY-MM-DD'

        Returns:
            DataFrame avec colonnes OHLCV, index de type datetime
        """
        pass


class YahooFinanceSource(DataSource):
    """
    Adapteur pour Yahoo Finance via yfinance.
    """

    def telecharger(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Télécharge les données depuis Yahoo Finance.

        Args:
            ticker: Symbole boursier (ex: 'AAPL')
            start_date: Date de début au format 'YYYY-MM-DD'
            end_date: Date de fin au format 'YYYY-MM-DD'

        Returns:
            DataFrame avec colonnes OHLCV, index de type datetime
            
        Raises:
            ValueError: Si le ticker est invalide ou aucune donnée disponible
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


class CSVDataSource(DataSource):
    """
    Adapteur pour lire des données depuis un fichier CSV local.
    """

    def __init__(self, chemin_csv: str):
        """
        Initialise la source CSV.

        Args:
            chemin_csv: Chemin vers le fichier CSV
        """
        self.chemin_csv = Path(chemin_csv)
        # Vérifie si le chemin existe
        if not self.chemin_csv.exists():
            raise FileNotFoundError(f"Fichier CSV introuvable : {chemin_csv}")

    def telecharger(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Lit les données depuis un fichier CSV local.
        Ignore ticker/start_date/end_date — lit tout le fichier.

        Args:
            ticker: Non utilisé (présent pour respecter l'interface)
            start_date: Non utilisé (présent pour respecter l'interface)
            end_date: Non utilisé (présent pour respecter l'interface)

        Returns:
            DataFrame avec colonnes OHLCV, index de type datetime
            
        Raises:
            FileNotFoundError: Si le fichier CSV n'existe pas
        """
        return pd.read_csv(self.chemin_csv, index_col=0, parse_dates=True)