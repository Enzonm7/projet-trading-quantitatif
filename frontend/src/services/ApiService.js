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
}

export default ApiService