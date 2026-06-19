from datetime import datetime, timedelta
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database.base import get_db
from backend.app.database.models import OHLCVData
from backend.app.core.data_fetcher import DataFetcher
from backend.app.core.data_source import YahooFinanceSource

router = APIRouter()

PERIODES_VALIDES = {"1mo", "3mo", "6mo", "1y", "2y", "5y"}


def _periode_vers_dates(periode: str) -> tuple[str, str]:
    """Convertit une période (ex: '1y') en dates debut/fin.

    Args:
        periode (str): Période parmi PERIODES_VALIDES

    Returns:
        tuple[str, str]: (date_debut, date_fin) au format 'YYYY-MM-DD'
    """
    date_fin = datetime.today()
    deltas = {
        "1mo": timedelta(days=30), 
        "3mo": timedelta(days=90), 
        "6mo": timedelta(days=180), 
        "1y": timedelta(days=365), 
        "2y": timedelta(days=730), 
        "5y": timedelta(days=1825)
    }
    date_debut = date_fin - deltas[periode]
    return date_debut.strftime("%Y-%m-%d"), date_fin.strftime("%Y-%m-%d")


def _sauvegarder_en_db(df: pd.DataFrame, ticker: str, db: Session) -> None:
    """Sauvegarde un DataFrame OHLCV en base de données.

    Args:
        df (pd.DataFrame): Données OHLCV avec index datetime
        ticker (str): Symbole boursier
        db (Session): Session SQLAlchemy
    """
    for date, ligne in df.iterrows():
        enregistrement = OHLCVData(
            ticker=ticker,
            date=date.to_pydatetime(),
            open=float(ligne["Open"]),
            high=float(ligne["High"]),
            low=float(ligne["Low"]),
            close=float(ligne["Close"]),
            volume=int(ligne["Volume"]),
        )
        db.add(enregistrement)
    db.commit()


@router.get("/stocks/{ticker}")
def lire_action(ticker: str, periode: str = "1y", db: Session = Depends(get_db)):
    """Retourne les données OHLCV d'une action.

    Cherche d'abord en DB, sinon télécharge via yfinance et sauvegarde.

    Args:
        ticker (str): Symbole boursier (ex: 'AAPL')
        periode (str): Période de données ('1mo','3mo','6mo','1y','2y','5y')
        db (Session): Session DB injectée par FastAPI

    Returns:
        dict: Ticker, période, nombre de points, et liste des données OHLCV

    Raises:
        HTTPException 400: Période invalide
        HTTPException 404: Ticker introuvable
    """
    # Validation de la période
    if periode not in PERIODES_VALIDES:
        raise HTTPException(
            status_code=400,
            detail=f"Période invalide. Valeurs acceptées : {PERIODES_VALIDES}"
        )
    
    ticker = ticker.upper()
    date_debut, date_fin = _periode_vers_dates(periode)

    # --- Tentative depuis la DB ---
    donnees_db = (
        db.query(OHLCVData)
        .filter(OHLCVData.ticker == ticker)
        .order_by(OHLCVData.date)
        .all()
    )

    if donnees_db:
        return {
            "ticker": ticker,
            "periode": periode,
            "source": "database",
            "nombre_points": len(donnees_db),
            "donnees": [
                {
                    "date": str(enr.date),
                    "open": enr.open,
                    "high": enr.high,
                    "low": enr.low,
                    "close": enr.close,
                    "volume": enr.volume,
                }
                for enr in donnees_db
            ]
        }
    
    # --- Fallback yfinance ---
    try:
        source = YahooFinanceSource()
        fetcher = DataFetcher(source=source)
        df = fetcher.get_cached_data(ticker, date_debut, date_fin)
    except Exception as e:
        print(f"ERREUR yfinance: {e}")
        raise HTTPException(
            status_code=404,
            detail=f"Ticker '{ticker}' introuvable ou données indisponibles."
        )
    
    # Sauvegarde pour les prochaines requêtes
    _sauvegarder_en_db(df, ticker, db)

    return {
        "ticker": ticker,
        "periode": periode,
        "source": "yfinance",
        "nombre_points": len(df),
        "donnees": [
            {
                "date": str(date.date()),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"]),
            }
            for date, row in df.iterrows()
        ]
    }