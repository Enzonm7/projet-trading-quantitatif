import Card from '../components/Card'

const metriques = [
  { label: 'Sharpe Ratio',   valeur: '—', detail: 'vs stratégie classique' },
  { label: 'Win Rate',       valeur: '—', detail: 'trades gagnants'        },
  { label: 'Max Drawdown',   valeur: '—', detail: 'perte max observée'     },
  { label: 'Paires actives', valeur: '—', detail: 'sur univers testé'      },
]

function Dashboard() {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold text-slate-800">Dashboard</h2>

      <div className="grid grid-cols-4 gap-4">
        {metriques.map((m) => (
          <Card key={m.label}>
            <p className="text-sm text-slate-500 mb-1">{m.label}</p>
            <p className="text-2xl font-semibold text-slate-800">{m.valeur}</p>
            <p className="text-xs text-slate-400 mt-1">{m.detail}</p>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Card>
          <p className="text-sm font-medium text-slate-700 mb-3">Paires détectées</p>
          <p className="text-sm text-slate-400 italic">Aucune donnée — lance une détection depuis Exploration</p>
        </Card>
        <Card>
          <p className="text-sm font-medium text-slate-700 mb-3">Signaux actifs</p>
          <p className="text-sm text-slate-400 italic">Aucun signal actif</p>
        </Card>
      </div>
    </div>
  )
}

export default Dashboard