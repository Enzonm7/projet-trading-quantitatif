"""
Module models - Modèles ORM SQLAlchemy pour la base de données pairs_trading.
"""

# Imports nécessaires depuis sqlalchemy :
from sqlalchemy import Column, Integer, Float, String, Boolean, Date, DateTime, BigInteger, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import relationship 
from backend.app.database.base import Base

# Modèle 1 : OHLCVData
class OHLCVData(Base):
    """Modèle représentant les données OHLCV d'un ticker."""

    __tablename__ = "ohlcv_data"
    __table_args__ = (UniqueConstraint('ticker', 'date'),) 
    id      = Column(Integer, primary_key=True)
    ticker  = Column(String(10), nullable=False)
    date    = Column(Date, nullable=False)
    open    = Column(Float, nullable=False)
    high    = Column(Float, nullable=False)
    low     = Column(Float, nullable=False)
    close   = Column(Float, nullable=False)
    volume  = Column(BigInteger, nullable=False)

class Pair(Base):
    """Modèle représentant une paire d'actifs corrélée et cointégrée."""

    __tablename__ = "pairs" 
    __table_args__ = (UniqueConstraint('ticker_a', 'ticker_b'),)
    id                  = Column(Integer, primary_key=True)
    ticker_a            = Column(String(10), nullable=False)
    ticker_b            = Column(String(10), nullable=False)
    correlation         = Column(Float, nullable=False)
    p_valeur            = Column(Float, nullable=False)
    ratio_couverture    = Column(Float, nullable=False)
    est_cointegree      = Column(Boolean, nullable=False)
    date_analyse        = Column(DateTime, default=func.now())
    backtests = relationship("Backtest", back_populates="pair")

class Backtest(Base):
    """Modèle représentant les résultats agrégés d'un backtest sur une paire."""

    __tablename__ = "backtests" 
    id                  = Column(Integer, primary_key=True)
    pair_id             = Column(Integer, ForeignKey('pairs.id', ondelete='CASCADE'))
    start_date          = Column(Date, nullable=False)
    end_date            = Column(Date, nullable=False)
    capital_initial     = Column(Float, nullable=False)
    rendement_total     = Column(Float, nullable=True)
    sharpe_ratio        = Column(Float, nullable=True)
    max_drawdown        = Column(Float, nullable=True)
    win_rate            = Column(Float, nullable=True)
    nombre_trades       = Column(Float, nullable=True)
    created_at          = Column(DateTime, default=func.now())
    pair    = relationship("Pair", back_populates="backtests")
    trades  = relationship("Trade", back_populates="backtest")

class Trade(Base):    
    """Modèle représentant un trade individuel issu d'un backtest."""

    __tablename__ = "trades" 
    id              = Column(Integer, primary_key=True)
    backtest_id     = Column(Integer, ForeignKey('backtests.id', ondelete='CASCADE'))
    date            = Column(Date, nullable=False)
    position        = Column(Integer, nullable=False)
    pnl_quotidien   = Column(Float, nullable=False)
    pnl_cumule      = Column(Float, nullable=False)
    capital         = Column(Float, nullable=False)
    backtest = relationship("Backtest", back_populates="trades")