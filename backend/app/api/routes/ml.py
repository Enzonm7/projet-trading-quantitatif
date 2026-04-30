"""Routes API pour le module Machine Learning."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.app.core.strategies import ZScoreReversionStrategy, MLEnhancedStrategy
from backend.app.core.backtester import Backtester
from backend.app.core.data_fetcher import DataFetcher
from backend.app.core.data_source import YahooFinanceSource
from backend.app.ml.xgboost_classifier import XGBoostClassifier
from backend.app.ml.feature_engineer import FeatureEngineer
from backend.app.ml.dataset_builder import DatasetBuilder

router = APIRouter(prefix="/ml", tags=["ml"])


class ComparaisonRequest(BaseModel):
    ticker_a: str
    ticker_b: str
    start_date: str
    end_date: str


@router.post("/comparison")
def comparer_strategies(request: ComparaisonRequest):
    """
    Entraîne XGBoost sur les données de la paire puis compare
    stratégie classique vs ML-Enhanced.
    Retourne les métriques des deux stratégies et l'amélioration du Sharpe.
    """
    try:
        # 1. Télécharger les données
        fetcher = DataFetcher(source=YahooFinanceSource())
        donnees = fetcher.download_pair(request.ticker_a, request.ticker_b, request.start_date, request.end_date)
        prix_a = donnees[f'Close_{request.ticker_a}']
        prix_b = donnees[f'Close_{request.ticker_b}']

        # 2. Préparer le dataset ML
        feature_engineer = FeatureEngineer()
        dataset_builder = DatasetBuilder(feature_engineer=feature_engineer)
        df_signaux = ZScoreReversionStrategy().generer_signaux(prix_a, prix_b)
        df_signaux['Close'] = prix_a.values
        df_train, df_val, df_test = dataset_builder.preparer_dataset(df_signaux)
        # 3. Entraîner XGBoost
        colonnes_features = ['rsi', 'bb_upper', 'bb_middle', 'bb_lower', 'volatilite', 'spread', 'zscore']
        classificateur = XGBoostClassifier()
        classificateur.train(df_train[colonnes_features], df_train['target'])
        # 4. Instancier MLEnhancedStrategy
        strategie_base = ZScoreReversionStrategy()
        strategie_ml = MLEnhancedStrategy(strategie_base=strategie_base, classificateur=classificateur, feature_engineer=feature_engineer)
        # 5. Appeler pipeline.comparer_strategies()
        strategie_classique = ZScoreReversionStrategy()
        backtester_classique = Backtester(strategy=strategie_classique)
        backtester_ml = Backtester(strategy=strategie_ml)
        resultats_classique = backtester_classique.executer_backtest(prix_a, prix_b)
        resultats_ml = backtester_ml.executer_backtest(prix_a, prix_b)
        # 6. Retourner la comparaison
        return {
            'classique': resultats_classique['metriques'],
            'ml_enhanced': resultats_ml['metriques'],
            'amelioration_sharpe': round(resultats_ml['metriques']['sharpe_ratio'] - resultats_classique['metriques']['sharpe_ratio'], 2)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/xgboost/metrics")
def obtenir_metriques_xgboost(request: ComparaisonRequest):
    """
    Entraîne XGBoost et retourne les métriques d'évaluation du modèle
    (accuracy, precision, recall, f1, roc_auc).
    """
    try:
        # 1. Télécharger les données
        fetcher = DataFetcher(source=YahooFinanceSource())
        donnees = fetcher.download_pair(request.ticker_a, request.ticker_b, request.start_date, request.end_date)
        prix_a = donnees[f'Close_{request.ticker_a}']
        prix_b = donnees[f'Close_{request.ticker_b}']
        # 2. Préparer le dataset ML
        feature_engineer = FeatureEngineer()
        dataset_builder = DatasetBuilder(feature_engineer=feature_engineer)
        df_signaux = ZScoreReversionStrategy().generer_signaux(prix_a, prix_b)
        df_signaux['Close'] = prix_a.values
        df_train, df_val, df_test = dataset_builder.preparer_dataset(df_signaux)
        # 3. Entraîner sur df_train
        colonnes_features = ['rsi', 'bb_upper', 'bb_middle', 'bb_lower', 'volatilite', 'spread', 'zscore']
        classificateur = XGBoostClassifier()
        classificateur.train(df_train[colonnes_features], df_train['target'])
        # 4. Évaluer sur df_test via classificateur.evaluer()
        metriques = classificateur.evaluer(df_test[colonnes_features], df_test['target'])
        # 5. Retourner les métriques
        return metriques
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))