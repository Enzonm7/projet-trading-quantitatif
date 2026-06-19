import { useState, useEffect } from 'react'
import Card from '../components/Card'
import Button from '../components/Button'
import ApiService from '../services/ApiService'
import { usePair } from '../context/PairContext'
import { PageTitle, SectionTitle, MetricCard, Badge, FormGrid, InputGroup, ErreurMsg } from '../components/UI'

function Backtest() {
  const { paireSelectionnee, setPaireSelectionnee } = usePair()

  const [tickerA, setTickerA]     = useState(paireSelectionnee.tickerA)
  const [tickerB, setTickerB]     = useState(paireSelectionnee.tickerB)
  const [dateDebut, setDateDebut] = useState(paireSelectionnee.dateDebut)
  const [dateFin, setDateFin]     = useState(paireSelectionnee.dateFin)
  const [capital, setCapital]     = useState(paireSelectionnee.capital)
  const [chargement, setChargement] = useState(false)
  const [resultats, setResultats] = useState(null)
  const [erreur, setErreur]       = useState(null)

  // Sync si le contexte change (navigation depuis Exploration)
  useEffect(() => {
    setTickerA(paireSelectionnee.tickerA)
    setTickerB(paireSelectionnee.tickerB)
    setDateDebut(paireSelectionnee.dateDebut)
    setDateFin(paireSelectionnee.dateFin)
    setCapital(paireSelectionnee.capital)
  }, [paireSelectionnee])

  const lancerBacktest = async () => {
    setChargement(true)
    setErreur(null)
    setResultats(null)
    // Mémorise la config dans le contexte pour les autres pages
    setPaireSelectionnee({ tickerA, tickerB, dateDebut, dateFin, capital })
    try {
      const reponse = await ApiService.lancerBacktest(tickerA, tickerB, dateDebut, dateFin, capital)
      setResultats(reponse.data)
    } catch {
      setErreur("Erreur lors du backtest. Vérifie que l'API est démarrée.")
    } finally {
      setChargement(false)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <PageTitle titre="Backtest" sous="Simulation historique · Z-Score Reversion Strategy" />

      <Card>
        <SectionTitle>Configuration</SectionTitle>
        <FormGrid cols={3}>
          <InputGroup label="Ticker A">
            <input type="text" value={tickerA} onChange={(e) => setTickerA(e.target.value.toUpperCase())} />
          </InputGroup>
          <InputGroup label="Ticker B">
            <input type="text" value={tickerB} onChange={(e) => setTickerB(e.target.value.toUpperCase())} />
          </InputGroup>
          <InputGroup label="Capital initial (€)">
            <input type="number" value={capital} onChange={(e) => setCapital(parseFloat(e.target.value))} />
          </InputGroup>
          <InputGroup label="Date début">
            <input type="date" value={dateDebut} onChange={(e) => setDateDebut(e.target.value)} />
          </InputGroup>
          <InputGroup label="Date fin">
            <input type="date" value={dateFin} onChange={(e) => setDateFin(e.target.value)} />
          </InputGroup>
          <InputGroup label=" ">
            <Button onClick={lancerBacktest} disabled={chargement} style={{ width: '100%' }}>
              {chargement ? 'Calcul...' : 'Lancer le backtest →'}
            </Button>
          </InputGroup>
        </FormGrid>
        <ErreurMsg message={erreur} />
      </Card>

      {resultats && (
        <Card>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <span style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '1px' }}>
              Résultats — {resultats.ticker_a} / {resultats.ticker_b}
            </span>
            <Badge variante={resultats.est_cointegree ? 'green' : 'red'}>
              {resultats.est_cointegree ? 'Cointégrée ✓' : 'Non cointégrée ✗'}
            </Badge>
            <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
              p-value : {resultats.p_valeur}
            </span>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px' }}>
            <MetricCard label="Rendement total" valeur={`${resultats.metriques.rendement_total} %`} couleur={resultats.metriques.rendement_total >= 0 ? 'green' : 'red'} />
            <MetricCard label="Sharpe Ratio"    valeur={resultats.metriques.sharpe_ratio} />
            <MetricCard label="Max Drawdown"    valeur={`${resultats.metriques.max_drawdown} %`} couleur="red" />
            <MetricCard label="Win Rate"        valeur={`${resultats.metriques.win_rate} %`} />
          </div>
        </Card>
      )}
    </div>
  )
}

export default Backtest
