import { useState } from 'react'
import Card from '../components/Card'
import Button from '../components/Button'
import ApiService from '../services/ApiService'

function MLInsights() {
  const [tickerA, setTickerA] = useState('AAPL')
  const [tickerB, setTickerB] = useState('MSFT')
  const [dateDebut, setDateDebut] = useState('2020-01-01')
  const [dateFin, setDateFin] = useState('2024-01-01')
  const [chargement, setChargement] = useState(false)
  const [metriquesML, setMetriquesML] = useState(null)
  const [comparaison, setComparaison] = useState(null)
  const [erreur, setErreur] = useState(null)

  const lancerAnalyse = async () => {
    setChargement(true)
    setErreur(null)
    setMetriquesML(null)
    setComparaison(null)
    try {
      const [repML, repComp] = await Promise.all([
        ApiService.obtenirMetriquesXGBoost(tickerA, tickerB, dateDebut, dateFin),
        ApiService.comparerStrategies(tickerA, tickerB, dateDebut, dateFin),
      ])
      setMetriquesML(repML.data)
      setComparaison(repComp.data)
    } catch (e) {
      setErreur("Erreur lors de l'analyse ML. Vérifie que l'API est démarrée.")
    } finally {
      setChargement(false)
    }
  }

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold text-slate-800">ML Insights</h2>

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
          <div className="flex items-end">
            <Button onClick={lancerAnalyse} disabled={chargement} className="w-full">
              {chargement ? 'Analyse en cours...' : 'Lancer l\'analyse ML'}
            </Button>
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
        </div>
        {erreur && <p className="text-sm text-red-500">{erreur}</p>}
      </Card>

      {metriquesML && (
        <Card>
          <p className="text-sm font-medium text-slate-700 mb-4">Métriques XGBoost</p>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
            {[
              { label: 'Accuracy', value: `${(metriquesML.accuracy * 100).toFixed(1)} %` },
              { label: 'Precision', value: `${(metriquesML.precision * 100).toFixed(1)} %` },
              { label: 'Recall', value: `${(metriquesML.recall * 100).toFixed(1)} %` },
              { label: 'F1 Score', value: `${(metriquesML.f1 * 100).toFixed(1)} %` },
              { label: 'ROC-AUC', value: metriquesML.roc_auc.toFixed(3) },
            ].map(({ label, value }) => (
              <div key={label} className="bg-slate-50 rounded-lg p-3 text-center">
                <p className="text-xs text-slate-500 mb-1">{label}</p>
                <p className="text-xl font-semibold text-slate-800">{value}</p>
              </div>
            ))}
          </div>
        </Card>
      )}

      {comparaison && (
        <Card>
          <p className="text-sm font-medium text-slate-700 mb-4">
            Comparaison Classique vs ML-Enhanced
            <span className={`ml-3 text-xs font-medium px-2 py-1 rounded-full ${
              comparaison.amelioration_sharpe >= 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
            }`}>
              Sharpe {comparaison.amelioration_sharpe >= 0 ? '+' : ''}{comparaison.amelioration_sharpe}
            </span>
          </p>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-xs text-slate-500 border-b border-slate-100">
                  <th className="text-left py-2 pr-6">Métrique</th>
                  <th className="text-right py-2 pr-6">Classique</th>
                  <th className="text-right py-2 pr-6">ML-Enhanced</th>
                  <th className="text-right py-2">Δ</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { label: 'Rendement total', key: 'rendement_total', suffix: ' %' },
                  { label: 'Sharpe Ratio', key: 'sharpe_ratio', suffix: '' },
                  { label: 'Max Drawdown', key: 'max_drawdown', suffix: ' %' },
                  { label: 'Win Rate', key: 'win_rate', suffix: ' %' },
                  { label: 'Nombre de trades', key: 'nombre_trades', suffix: '' },
                ].map(({ label, key, suffix }) => {
                  const delta = (comparaison.ml_enhanced[key] - comparaison.classique[key]).toFixed(2)
                  const positif = parseFloat(delta) >= 0
                  const estDrawdown = key === 'max_drawdown'
                  const amelioration = estDrawdown ? !positif : positif
                  return (
                    <tr key={key} className="border-b border-slate-50 hover:bg-slate-50">
                      <td className="py-2 pr-6 text-slate-600">{label}</td>
                      <td className="py-2 pr-6 text-right text-slate-700">{comparaison.classique[key]}{suffix}</td>
                      <td className="py-2 pr-6 text-right font-medium text-slate-800">{comparaison.ml_enhanced[key]}{suffix}</td>
                      <td className={`py-2 text-right text-xs font-medium ${amelioration ? 'text-green-600' : 'text-red-500'}`}>
                        {positif ? '+' : ''}{delta}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  )
}

export default MLInsights