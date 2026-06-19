# PairLens — ML-Enhanced Pairs Trading Platform

> A full-stack statistical arbitrage platform that combines classical pairs-trading theory (cointegration, OLS hedge ratios, z-score mean reversion) with a machine learning filtering layer (XGBoost) to evaluate whether ML can improve signal quality over a purely statistical baseline.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688)
![React](https://img.shields.io/badge/React-18-61DAFB)
![XGBoost](https://img.shields.io/badge/XGBoost-3.x-brightgreen)
![Status](https://img.shields.io/badge/status-academic%20project-orange)

This is an academic project developed over 8 months (October 2025 – May 2026) as part of the *Licence Sciences du Numérique* at École Du Numérique. It is intended both as a graded deliverable and as a learning vehicle for software engineering practices, quantitative finance, and applied machine learning.

---

## Table of Contents

- [Overview](#overview)
- [Quantitative Methodology](#quantitative-methodology)
- [System Architecture](#system-architecture)
- [Machine Learning Pipeline](#machine-learning-pipeline)
- [Risk Management](#risk-management)
- [Results](#results)
- [Disclaimer](#disclaimer)
- [Installation](#installation)
- [Running Tests](#running-tests)
- [Demo Notebook](#demo-notebook)
- [Project Structure](#project-structure)
- [Known Limitations & Roadmap](#known-limitations--roadmap)
- [Tech Stack](#tech-stack)
- [Author & Context](#author--context)

---

## Overview

Pairs trading is a market-neutral statistical arbitrage strategy: two historically correlated assets are monitored for temporary divergence, with the expectation that their relationship will revert to its historical equilibrium. PairLens implements this strategy end-to-end — from raw price data to a tradable signal — and adds an XGBoost classification layer on top of the classical signal to test whether it improves risk-adjusted performance.

The platform is organized into three layers:

1. **Backtesting Engine** — cointegration testing, signal generation, trade simulation, performance metrics
2. **ML Prediction Layer** — feature engineering and an XGBoost classifier that filters the classical signal
3. **Interactive Dashboard** — a React frontend for exploring pairs, running backtests, and inspecting ML insights

---

## Quantitative Methodology

The signal engine follows a standard statistical arbitrage workflow:

1. **Cointegration testing (Engle-Granger, two-step approach).** For a candidate pair, an OLS regression of `log(price_A)` on `log(price_B)` yields the **hedge ratio**. The residual of that regression (the *spread*) is tested for stationarity with an Augmented Dickey-Fuller test. A pair is considered valid only if the spread's ADF p-value falls below the configured threshold (default: 0.05).

2. **Log-returns over raw prices.** Prices are log-transformed before the regression and spread calculation. This keeps the spread stationary and the resulting z-score statistically meaningful — raw price spreads between assets with different price scales and growth rates are not directly comparable over time.

3. **Z-score mean reversion signal.** The spread is normalized into a rolling z-score (default window: 20 days). A long/short signal is triggered when the z-score crosses an entry threshold (default ±2.0) and closed when it reverts inside an exit band (default ±0.5).

4. **ML-enhanced filtering.** An XGBoost classifier predicts, for each candidate entry, whether the spread is likely to *converge* or *diverge* over the next N days. The classical signal is only acted upon when the model confirms convergence — the ML layer is a filter on top of the statistical signal, not a replacement for it.

This design choice is deliberate: it keeps the statistically interpretable core (cointegration, hedge ratio, z-score) as the foundation, and uses ML only where it adds value — reducing false-positive entries — rather than as a black-box signal generator.

---

## System Architecture

```
                 ┌─────────────────┐
                 │   React Frontend │  (Dashboard, Exploration, Backtest,
                 │   (Vite + Recharts)│  Performance, ML Insights)
                 └────────┬─────────┘
                          │ REST (axios)
                 ┌────────▼─────────┐
                 │   FastAPI Backend │
                 │  /api/stocks      │
                 │  /api/pairs       │
                 │  /api/ml          │
                 └────────┬─────────┘
                          │
        ┌─────────────────┼──────────────────┐
        │                 │                  │
┌───────▼──────┐  ┌───────▼────────┐  ┌──────▼───────┐
│ Core Engine   │  │  ML Pipeline    │  │  PostgreSQL   │
│ DataFetcher   │  │ FeatureEngineer │  │  (SQLAlchemy) │
│ PairsSelector │  │ DatasetBuilder  │  │  ohlcv_data   │
│ Backtester    │  │ XGBoostClassifier│ │  pairs        │
│ RiskManager   │  │                 │  │  backtests    │
└───────────────┘  └─────────────────┘  └───────────────┘
```

### Backend design

- **`DataSource` (abstract) → `YahooFinanceSource` / `CSVDataSource`** — an adapter pattern that decouples the rest of the system from the data provider. `DataFetcher` wraps any `DataSource` with a local CSV cache.
- **`Strategy` (abstract) → `ZScoreReversionStrategy` → `MLEnhancedStrategy`** — the trading logic is injected into the `Backtester` rather than hardcoded, so the classical and ML-enhanced strategies can be benchmarked against each other with the exact same execution engine.
- **`Backtester`** — simulates daily P&L from a signal series, and computes Sharpe ratio, max drawdown, win rate, and total return.
- **`RiskManager`** — volatility-adjusted position sizing, global and per-position stop-loss, and dynamic leverage adjustment based on realized Sharpe ratio.
- **FastAPI** exposes three routers (`stocks`, `pairs`, `ml`) backed by a PostgreSQL database (`ohlcv_data`, `pairs`, `backtests`, `trades` tables via SQLAlchemy ORM).

### Frontend design

- **React + Vite**, five pages (`Dashboard`, `Exploration`, `Backtest`, `Performance`, `ML Insights`) sharing state through a `PairContext`.
- **Recharts** for equity curves, spread/z-score visualization, and feature importance charts.
- **`ApiService`** centralizes all HTTP calls to the backend.

> *Architecture diagrams (backend class diagram, frontend component diagram, Gantt chart) are available in [`/docs`](./docs) — insert your exported PNGs there and reference them here, e.g. `![Backend architecture](./docs/backend_class_diagram.png)`.*

---

## Machine Learning Pipeline

```
FeatureEngineer → DatasetBuilder → XGBoostClassifier
```

1. **`FeatureEngineer`** computes technical indicators from raw prices: RSI, Bollinger Bands, rolling annualized volatility, and rolling correlation.
2. **`DatasetBuilder`** labels each observation based on **forward-looking convergence**: for a given day *t*, if `|zscore[t+horizon]| < |zscore[t]|`, the spread is converging (label 1), otherwise diverging (label 0). The dataset is then split **chronologically** into 70% train / 15% validation / 15% test — a strict temporal split with no shuffling, which avoids look-ahead bias (the model never trains on data that occurs after what it is evaluated on).
3. **`XGBoostClassifier`** standardizes features, trains a gradient-boosted classifier, and supports hyperparameter optimization via `GridSearchCV` with `TimeSeriesSplit` cross-validation (rather than standard k-fold, again to respect temporal ordering).

A full walkthrough with code examples is available in [`backend/app/ml/README.md`](./backend/app/ml/README.md).

**Why XGBoost over LSTM?** XGBoost was chosen as the primary model for its training speed, robustness on tabular/indicator-style features, and interpretability via feature importance — all useful properties at this stage of the project. An LSTM-based predictor was scoped in the original design (see [Known Limitations](#known-limitations--roadmap)) but has not been implemented.

---

## Risk Management

Beyond signal generation, the platform applies a basic risk layer on top of simulated trades:

- **Position sizing**, optionally adjusted for volatility (higher volatility → smaller position).
- **Stop-loss**, both globally (on total capital drawdown) and per individual position.
- **Dynamic leverage**, scaled up only when the realized Sharpe ratio exceeds 1.0, capped at a configurable maximum.
- **Risk metrics**: maximum loss, daily return volatility, 95% Value-at-Risk, and gain/loss ratio.

---

## Results

> **To complete before submission:** run a backtest on your reference pair(s) and report the actual output here. Do not estimate or approximate these numbers — they should come directly from `pipeline.generer_rapport()` or the `/api/ml/comparison` endpoint.

Suggested format:

| Strategy | Sharpe Ratio | Total Return | Max Drawdown | Win Rate |
|---|---|---|---|---|
| Z-Score (classical) | — | — | — | — |
| ML-Enhanced (XGBoost) | — | — | — | — |

XGBoost evaluation metrics (from `XGBoostClassifier.evaluer()`):

| Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|
| — | — | — | — | — |

**Important methodological caveats:**
- The backtester does **not** model transaction costs or slippage — reported returns are gross, not net of trading frictions.
- Results reflect a single historical period on a small universe of tickers; they are not a robustness guarantee out-of-sample or across regimes.
- With a small candidate universe, finding only one or two cointegrated pairs in a given period is an expected and statistically valid outcome — it reflects the strictness of the cointegration test, not a bug.

---

## Disclaimer

This project was built for academic and educational purposes as part of a university curriculum. It does not constitute financial or investment advice, and the strategies implemented have not been validated for live trading. Use at your own risk.

---

## Installation

### Prerequisites
- Python 3.10+
- Node.js 18+ (frontend)
- PostgreSQL 14+ running locally (or update `DATABASE_URL` to point elsewhere)

### Backend

```bash
# From the project root
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt

# Configure the database connection
echo "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/pairs_trading_db" > .env

# Run the API — must be launched from the project root
uvicorn backend.app.api.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`, with interactive docs at `http://127.0.0.1:8000/docs`.

> **Note:** the API must be started from the project root (not from inside `backend/`) — all internal imports are absolute paths rooted at `backend.app.*`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The dashboard will be available at `http://localhost:5173` and expects the API at `http://localhost:8000` (see `frontend/src/services/ApiService.js` to change this).

---

## Running Tests

```bash
# From the project root
pytest backend/tests/ -v

# With coverage
pytest backend/tests/ --cov=backend/app --cov-report=term-missing
```

The test suite (150 tests across unit and integration layers, using synthetic data and fakes rather than live network calls) currently passes at **148/150**, with **79% line coverage** on the backend. The 2 remaining tests exercise a route that requires a live PostgreSQL connection and are environment-dependent rather than indicative of a code defect.

---

## Demo Notebook

[`notebooks/01_demonstration_pipeline.ipynb`](./notebooks/01_demonstration_pipeline.ipynb) walks through the full pipeline end-to-end on a live example: pipeline configuration, a single-pair backtest with visualizations (normalized prices, spread, z-score, equity curve, return distribution), and a multi-pair comparison ranked by Sharpe ratio.

```bash
jupyter notebook notebooks/01_demonstration_pipeline.ipynb
```

---

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── core/          # DataFetcher, DataSource, PairsSelector, Backtester, RiskManager, Strategy
│   │   ├── ml/             # FeatureEngineer, DatasetBuilder, XGBoostClassifier (+ module README)
│   │   ├── database/       # SQLAlchemy models & session
│   │   ├── api/            # FastAPI app & routes (stocks, pairs, ml)
│   │   └── pipeline.py      # TradingPipeline orchestrator
│   ├── tests/
│   │   ├── unit/
│   │   └── integration/
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── pages/          # Dashboard, Exploration, Backtest, Performance, MLInsights
│       ├── components/     # PairsList, Sidebar, Card, Button, Layout, Header
│       ├── context/        # PairContext (shared state)
│       └── services/       # ApiService
├── notebooks/
│   └── 01_demonstration_pipeline.ipynb
└── README.md
```

---

## Known Limitations & Roadmap

What's implemented and tested:
- Cointegration-based pair selection, z-score signal generation, backtesting, and risk management
- Full ML pipeline (feature engineering → temporal dataset split → XGBoost training/evaluation/optimization)
- REST API with PostgreSQL persistence
- React dashboard across 5 pages

What's explicitly out of scope at this stage:
- **LSTM predictor** — scoped in the original design, not implemented (XGBoost was prioritized; see [ML Pipeline](#machine-learning-pipeline))
- **Transaction costs / slippage modeling** in the backtester
- **Frontend test coverage** (Jest) — backend is tested, frontend is not yet
- **Docker deployment** — optional per the original project scope, not yet packaged

---

## Tech Stack

| Layer | Technologies |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy, PostgreSQL |
| Data & Stats | pandas, NumPy, statsmodels, SciPy, yfinance |
| Machine Learning | XGBoost, scikit-learn |
| Frontend | React, Vite, react-router-dom, axios, Recharts |
| Testing | pytest, pytest-cov |

---

## Author & Context

Developed by **Enzo NZENGUE MAYILA** as part of the *Licence Sciences du Numérique* at Catholic University of Lille (October 2025 – May 2026), supervised with monthly sprint reviews and a final oral defense.

<!-- TODO: add contact / LinkedIn / GitHub links -->
<!-- TODO: decide on a license (MIT is the common default for portfolio projects; confirm this is consistent with your school's policy on academic project ownership before adding a LICENSE file) -->