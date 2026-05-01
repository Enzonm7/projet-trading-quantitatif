import axios from 'axios'

const BASE_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

const ApiService = {
  // Stocks
  obtenirDonneesAction: (ticker) => api.get(`/api/stocks/${ticker}`),

  // Pairs
  detecterPaires: (tickers, dateDebut, dateFin) =>
    api.post('/api/pairs/detect', { tickers, date_debut: dateDebut, date_fin: dateFin }),

  obtenirPaires: () => api.get('/api/pairs'),

  // Health
  verifierSante: () => api.get('/health'),

  // Backtest
  lancerBacktest: (ticker_a, ticker_b, dateDebut, dateFin, capitalInitial) =>
    api.post('/api/pairs/backtest', {
      ticker_a,
      ticker_b,
      date_debut: dateDebut,
      date_fin: dateFin,
      capital_initial: capitalInitial,
    }),

  // ML
  obtenirMetriquesXGBoost: (ticker_a, ticker_b, dateDebut, dateFin) =>
    api.post('/api/ml/xgboost/metrics', { ticker_a, ticker_b, start_date: dateDebut, end_date: dateFin }),

  comparerStrategies: (ticker_a, ticker_b, dateDebut, dateFin) =>
    api.post('/api/ml/comparison', { ticker_a, ticker_b, start_date: dateDebut, end_date: dateFin }),
}

export default ApiService