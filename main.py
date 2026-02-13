from backend.app.core.data_source import YahooFinanceSource
from backend.app.core.data_fetcher import DataFetcher
from backend.app.core.pairs_selector import PairsSelector
from backend.app.core.strategies import ZScoreReversionStrategy
from backend.app.core.backtester import Backtester
from backend.app.core.risk_manager import RiskManager
from backend.app.pipeline import TradingPipeline

pipeline = TradingPipeline(
    fetcher=DataFetcher(source=YahooFinanceSource()),
    selector=PairsSelector(),
    backtester=Backtester(strategy=ZScoreReversionStrategy()),
    risk_manager=RiskManager()
)

resultats = pipeline.executer_backtest(
    ticker_a='AAPL',
    ticker_b='MSFT',
    start_date='2023-01-01',
    end_date='2024-01-01'
)

pipeline.generer_rapport(resultats)