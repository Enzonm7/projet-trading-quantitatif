# test_refactoring.py
from backend.app.core.data_fetcher import DataFetcher
from backend.app.core.pairs_selector import PairsSelector
from backend.app.core.backtester import Backtester
from backend.app.core.risk_manager import RiskManager
from backend.app.core.strategies import ZScoreReversionStrategy
from backend.app.pipeline import TradingPipeline

# 1. Instancier les modules avec injection de dépendances
fetcher = DataFetcher(cache_dir='./cache')
selector = PairsSelector(correlation_threshold=0.7, pvalue_threshold=0.05)

# 2. Créer la stratégie
strategy = ZScoreReversionStrategy(window=20, seuil_entree=2.0, seuil_sortie=0.5)

# 3. Créer le backtester avec la stratégie
backtester = Backtester(strategy=strategy, capital_initial=10000.0)

# 4. Créer le risk manager
risk_manager = RiskManager(max_position_size=0.1, stop_loss_pct=0.02)

# 5. Assembler le pipeline
pipeline = TradingPipeline(
    fetcher=fetcher,
    selector=selector,
    backtester=backtester,
    risk_manager=risk_manager
)

# 6. Tester sur une paire
print(" Lancement du backtest...")
resultats = pipeline.executer_backtest(
    ticker_a='AAPL',
    ticker_b='MSFT',
    start_date='2023-01-01',
    end_date='2024-01-01',
    appliquer_risk_management=True
)

# 7. Afficher les résultats
print("\n RÉSULTATS DU BACKTEST")
print(f"Paire: {resultats['ticker_a']} / {resultats['ticker_b']}")
print(f"Cointégration: {resultats['is_cointegrated']} (p-value: {resultats['p_value']:.4f})")
print(f"Ratio de couverture: {resultats['ratio_couverture']:.4f}")
print(f"\n MÉTRIQUES:")
for key, value in resultats['metriques'].items():
    print(f"  - {key}: {value}")

if resultats['metriques_risque']:
    print(f"\n MÉTRIQUES DE RISQUE:")
    for key, value in resultats['metriques_risque'].items():
        print(f"  - {key}: {value}")