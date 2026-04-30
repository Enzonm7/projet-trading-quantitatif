import { useState } from 'react'
import Card from '../components/Card'
import Button from '../components/Button'
import ApiService from '../services/ApiService'

function Backtest() {
  const [tickerA, setTickerA] = useState('AAPL')
  const [tickerB, setTickerB] = useState('MSFT')
  const [dateDebut, setDateDebut] = useState('2020-01-01')
  const [dateFin, setDateFin] = useState('2024-01-01')
  const [capital, setCapital] = useState(10000)
  const [chargement, setChargement] = useState(false)
  const [resultats, setResultats] = useState(null)
  const [erreur, setErreur] = useState(null)

  const lancerBacktest = async () => {
    setChargement(true)
    setErreur(null)
    setResultats(null)
    try {
      const reponse = await ApiService.lancerBacktest(tickerA, tickerB, dateDebut, dateFin, capital)
      setResultats(reponse.data)
    } catch (e) {
      setErreur("Erreur lors du backtest. Vérifie que l'API est démarrée.")
    } finally {
      setChargement(false)
    }
  }

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold text-slate-800">Backtest</h2>

      <Card>
        <p className="text-sm font-medium text-slate-700 mb-4">Configuration</p>
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-xs text-slate-500 mb-1">Ticker A</label>
            <input type="text" value={tickerA} onChange={(e) => setTickerA(e.target.value)}
              className="w-full border border-slate-200 rounded-md px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label className="block text-xs text-slate-500 mb-1">Ticker B</label>
            <input type="text" value={tickerB} onChange={(e) => setTickerB(e.target.value)}
              className="w-full border border-slate-200 rounded-md px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label className="block text-xs text-slate-500 mb-1">Capital initial (€)</label>
            <input type="number" value={capital} onChange={(e) => setCapital(parseFloat(e.target.value))}
              className="w-full border border-slate-200 rounded-md px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label className="block text-xs text-slate-500 mb-1">Date début</label>
            <input type="date" value={dateDebut} onChange={(e) => setDateDebut(e.target.value)}
              className="w-full border border-slate-200 rounded-md px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label className="block text-xs text-slate-500 mb-1">Date fin</label>
            <input type="date" value={dateFin} onChange={(e) => setDateFin(e.target.value)}
              className="w-full border border-slate-200 rounded-md px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div className="flex items-end">
            <Button onClick={lancerBacktest} disabled={chargement} className="w-full">
              {chargement ? 'Calcul...' : 'Lancer le backtest'}
            </Button>
          </div>
        </div>
        {erreur && <p className="text-sm text-red-500">{erreur}</p>}
      </Card>

      {resultats && (
        <Card>
          <p className="text-sm font-medium text-slate-700 mb-4">
            Résultats — {resultats.ticker_a} / {resultats.ticker_b}
          </p>
          <div className="mb-3">
            <span className={`text-xs font-medium px-2 py-1 rounded-full ${resultats.est_cointegree ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
              {resultats.est_cointegree ? 'Cointégrée ✓' : 'Non cointégrée ✗'}
            </span>
            <span className="text-xs text-slate-500 ml-2">p-value : {resultats.p_valeur}</span>
          </div>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            {[
              { label: 'Rendement total', value: `${resultats.metriques.rendement_total} %` },
              { label: 'Sharpe Ratio', value: resultats.metriques.sharpe_ratio },
              { label: 'Max Drawdown', value: `${resultats.metriques.max_drawdown} %` },
              { label: 'Win Rate', value: `${resultats.metriques.win_rate} %` },
            ].map(({ label, value }) => (
              <div key={label} className="bg-slate-50 rounded-lg p-3">
                <p className="text-xs text-slate-500">{label}</p>
                <p className="text-lg font-semibold text-slate-800">{value}</p>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  )
}

export default Backtest