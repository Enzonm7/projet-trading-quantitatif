"""Routes API pour la détection de paires cointégrées."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List
from sqlalchemy.orm import Session
import pandas as pd
from app.database.base import get_db
from app.core.data_fetcher import DataFetcher
from app.core.pairs_selector import PairsSelector
from app.core.data_source import YahooFinanceSource

router = APIRouter(tags=["pairs"])


# --- Schémas Pydantic ---

class DetectPairsRequest(BaseModel):
    """Corps de la requête pour détecter les paires."""
    tickers: List[str] = Field(..., min_length=2, description="Liste de tickers (min 2)")
    date_debut: str = Field(default="2020-01-01", description="Date de début YYYY-MM-DD")
    date_fin: str = Field(default="2024-01-01", description="Date de fin YYYY-MM-DD")
    seuil_correlation: float = Field(default=0.7, ge=0, le=1)
    seuil_pvalue: float = Field(default=0.05, ge=0, le=1)


class PaireResultat(BaseModel):
    """Résultat pour une paire détectée."""
    ticker_a: str
    ticker_b: str
    correlation: float
    p_valeur: float


class DetectPairsResponse(BaseModel):
    """Réponse de la route detect."""
    nombre_paires: int
    paires: List[PaireResultat]

class BacktestRequest(BaseModel):
    """Corps de la requête pour lancer un backtest."""
    ticker_a: str
    ticker_b: str
    date_debut: str = Field(default="2020-01-01")
    date_fin: str = Field(default="2024-01-01")
    capital_initial: float = Field(default=10000.0, gt=0)

class BacktestResponse(BaseModel):
    """Réponse du backtest."""
    ticker_a: str
    ticker_b: str
    est_cointegree: bool
    p_valeur: float
    metriques: dict
    equity_curve: list
    trades: list

# --- Route ---

@router.post("/pairs/detect", response_model=DetectPairsResponse)
def detecter_paires(
    requete: DetectPairsRequest,
    db: Session = Depends(get_db)
):
    """
    Détecte les paires corrélées et cointégrées parmi une liste de tickers.

    Args:
        requete: Corps JSON avec tickers et paramètres
        db: Session base de données

    Returns:
        DetectPairsResponse: Liste des paires valides avec leurs métriques
    """
    # 1. Récupérer les données
    source = YahooFinanceSource()
    fetcher = DataFetcher(source=source)

    donnees_prix = {}
    for ticker in requete.tickers:
        try:
            df = fetcher.get_cached_data(ticker, requete.date_debut, requete.date_fin)
            donnees_prix[ticker] = df["Close"]
        except Exception:
            raise HTTPException(
                status_code=404,
                detail=f"Impossible de récupérer les données pour {ticker}"
            )

    # 2. Construire DataFrame multi-colonnes
    df_prix = pd.DataFrame(donnees_prix).dropna()

    if df_prix.empty:
        raise HTTPException(status_code=400, detail="Aucune donnée commune sur la période")

    # 3. Calculer corrélations + cointégration
    selecteur = PairsSelector(
        correlation_threshold=requete.seuil_correlation,
        pvalue_threshold=requete.seuil_pvalue
    )

    matrice_corr = selecteur.calculate_correlation(df_prix)
    toutes_paires = selecteur.find_all_pairs(requete.tickers)

    paires_avec_stats = []
    for ticker_a, ticker_b in toutes_paires:
        correlation = matrice_corr.loc[ticker_a, ticker_b]
        _, p_valeur = selecteur.test_cointegration(
            df_prix[ticker_a],
            df_prix[ticker_b]
        )
        paires_avec_stats.append((ticker_a, ticker_b, correlation, p_valeur))

    # 4. Filtrer les paires valides
    paires_valides = selecteur.filter_valid_pairs(paires_avec_stats)

    # 5. Construire la réponse
    resultats = [
        PaireResultat(
            ticker_a=a,
            ticker_b=b,
            correlation=round(corr, 4),
            p_valeur=round(pval, 4)
        )
        for a, b, corr, pval in paires_valides
    ]

    return DetectPairsResponse(
        nombre_paires=len(resultats),
        paires=resultats
    )

@router.post("/pairs/backtest", response_model=BacktestResponse)
def lancer_backtest(requete: BacktestRequest):
    """Lance un backtest complet sur une paire."""
    try:
        from app.core.backtester import Backtester
        from app.core.strategies import ZScoreReversionStrategy
        from app.core.pairs_selector import PairsSelector

        fetcher = DataFetcher(source=YahooFinanceSource())
        donnees = fetcher.download_pair(
            requete.ticker_a, requete.ticker_b,
            requete.date_debut, requete.date_fin
        )
        prix_a = donnees[f'Close_{requete.ticker_a}']
        prix_b = donnees[f'Close_{requete.ticker_b}']

        selecteur = PairsSelector()
        est_cointegree, p_valeur = selecteur.test_cointegration(prix_a, prix_b)

        strategie = ZScoreReversionStrategy()
        backtester = Backtester(strategy=strategie, capital_initial=requete.capital_initial)
        resultats = backtester.executer_backtest(prix_a, prix_b)

        equity_curve = [
            {'date': str(date.date()), 'capital': round(capital, 2)}
            for date, capital in resultats['df_trades']['capital'].items()
        ]
        # Trades — uniquement les jours avec changement de position
        df_t = resultats['df_trades']
        changements = df_t[df_t['position'] != df_t['position'].shift(1)]
        trades = [
            {'date': str(date.date()), 'pnl': round(row['pnl_quotidien'], 2), 'position': int(row['position'])}
            for date, row in changements.iterrows()
        ]

        return BacktestResponse(
            ticker_a=requete.ticker_a,
            ticker_b=requete.ticker_b,
            est_cointegree=est_cointegree,
            p_valeur=round(p_valeur, 4),
            metriques=resultats['metriques'],
            equity_curve=equity_curve,
            trades=trades
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))