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