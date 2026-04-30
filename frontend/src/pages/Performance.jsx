import { useState } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import Card from '../components/Card'
import Button from '../components/Button'
import ApiService from '../services/ApiService'

function Performance() {
  const [tickerA, setTickerA] = useState('AAPL')
  const [tickerB, setTickerB] = useState('MSFT')
  const [dateDebut, setDateDebut] = useState('2020-01-01')
  const [dateFin, setDateFin] = useState('2024-01-01')
  const [capital, setCapital] = useState(10000)
  const [chargement, setChargement] = useState(false)
  const [resultats, setResultats] = useState(null)
  const [erreur, setErreur] = useState(null)

  const lancerAnalyse = async () => {
    setChargement(true)
    setErreur(null)
    setResultats(null)
    try {
      const reponse = await ApiService.lancerBacktest(tickerA, tickerB, dateDebut, dateFin, capital)
      setResultats(reponse.data)
    } catch (e) {
      setErreur("Erreur lors de l'analyse. Vérifie que l'API est démarrée.")
    } finally {
      setChargement(false)
    }
  }

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold text-slate-800">Performance</h2>

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
            <Button onClick={lancerAnalyse} disabled={chargement} className="w-full">
              {chargement ? 'Calcul...' : 'Analyser'}
            </Button>
          </div>
        </div>
        {erreur && <p className="text-sm text-red-500">{erreur}</p>}
      </Card>

      {resultats && (
        <>
          <Card>
            <p className="text-sm font-medium text-slate-700 mb-4">Equity Curve — {resultats.ticker_a} / {resultats.ticker_b}</p>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={resultats.equity_curve}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="date" tick={{ fontSize: 11 }}
                  tickFormatter={(v) => v.slice(0, 7)}
                  interval={Math.floor(resultats.equity_curve.length / 6)} />
                <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `${v.toLocaleString()} €`} />
                <Tooltip formatter={(v) => [`${v.toLocaleString()} €`, 'Capital']}
                  labelFormatter={(l) => `Date : ${l}`} />
                <Line type="monotone" dataKey="capital" stroke="#3b82f6" dot={false} strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Card>

          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            {[
              { label: 'Rendement total', value: `${resultats.metriques.rendement_total} %` },
              { label: 'Sharpe Ratio', value: resultats.metriques.sharpe_ratio },
              { label: 'Max Drawdown', value: `${resultats.metriques.max_drawdown} %` },
              { label: 'Win Rate', value: `${resultats.metriques.win_rate} %` },
            ].map(({ label, value }) => (
              <Card key={label}>
                <p className="text-xs text-slate-500">{label}</p>
                <p className="text-2xl font-semibold text-slate-800">{value}</p>
              </Card>
            ))}
          </div>

          <Card>
            <p className="text-sm font-medium text-slate-700 mb-3">
              Trades ({resultats.trades.length})
            </p>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-xs text-slate-500 border-b border-slate-100">
                    <th className="text-left py-2 pr-4">Date</th>
                    <th className="text-left py-2 pr-4">Position</th>
                    <th className="text-right py-2">PnL (€)</th>
                  </tr>
                </thead>
                <tbody>
                  {resultats.trades.map((trade, i) => (
                    <tr key={i} className="border-b border-slate-50 hover:bg-slate-50">
                      <td className="py-2 pr-4 text-slate-600">{trade.date}</td>
                      <td className="py-2 pr-4">
                        <span className={`text-xs px-2 py-0.5 rounded-full ${
                          trade.position === 1 ? 'bg-green-100 text-green-700' :
                          trade.position === -1 ? 'bg-red-100 text-red-700' :
                          'bg-slate-100 text-slate-500'}`}>
                          {trade.position === 1 ? 'Long' : trade.position === -1 ? 'Short' : 'Neutre'}
                        </span>
                      </td>
                      <td className={`py-2 text-right font-medium ${trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {trade.pnl >= 0 ? '+' : ''}{trade.pnl}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </>
      )}
    </div>
  )
}

export default Performance