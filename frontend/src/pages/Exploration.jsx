import { useState } from 'react'
import Card from '../components/Card'
import Button from '../components/Button'
import PairsList from '../components/PairsList'
import ApiService from '../services/ApiService'

function Exploration() {
  const [tickers, setTickers] = useState('AAPL,MSFT,JPM,BAC,PEP,KO')
  const [dateDebut, setDateDebut] = useState('2023-01-01')
  const [dateFin, setDateFin] = useState('2024-01-01')
  const [chargement, setChargement] = useState(false)
  const [paires, setPaires] = useState([])
  const [erreur, setErreur] = useState(null)

  const lancerDetection = async () => {
    setChargement(true)
    setErreur(null)
    setPaires([])

    try {
      const listeTickers = tickers.split(',').map((t) => t.trim())
      const reponse = await ApiService.detecterPaires(listeTickers, dateDebut, dateFin)
      setPaires(reponse.data.paires)
    } catch (e) {
      setErreur("Erreur lors de la détection. Vérifie que l'API est démarrée.")
    } finally {
      setChargement(false)
    }
  }

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold text-slate-800">Exploration</h2>

      <Card>
        <p className="text-sm font-medium text-slate-700 mb-4">Détection de paires</p>

        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="col-span-3">
            <label className="block text-xs text-slate-500 mb-1">
              Tickers (séparés par des virgules)
            </label>
            <input
              type="text"
              value={tickers}
              onChange={(e) => setTickers(e.target.value)}
              className="w-full border border-slate-200 rounded-md px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="AAPL,MSFT,JPM,BAC"
            />
          </div>

          <div>
            <label className="block text-xs text-slate-500 mb-1">Date début</label>
            <input
              type="date"
              value={dateDebut}
              onChange={(e) => setDateDebut(e.target.value)}
              className="w-full border border-slate-200 rounded-md px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs text-slate-500 mb-1">Date fin</label>
            <input
              type="date"
              value={dateFin}
              onChange={(e) => setDateFin(e.target.value)}
              className="w-full border border-slate-200 rounded-md px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="flex items-end">
            <Button
              onClick={lancerDetection}
              disabled={chargement}
              className="w-full"
            >
              {chargement ? 'Détection...' : 'Détecter les paires'}
            </Button>
          </div>
        </div>

        {erreur && (
          <p className="text-sm text-red-500">{erreur}</p>
        )}
      </Card>

      {paires.length > 0 && (
        <Card>
          <p className="text-sm font-medium text-slate-700 mb-3">
            Résultats — {paires.length} paire(s) détectée(s)
          </p>
          <PairsList paires={paires} />
        </Card>
      )}
    </div>
  )
}

export default Exploration