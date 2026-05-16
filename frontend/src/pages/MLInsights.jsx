import { useState, useEffect } from 'react'
import Card from '../components/Card'
import Button from '../components/Button'
import ApiService from '../services/ApiService'
import { usePair } from '../context/PairContext'
import { PageTitle, SectionTitle, MetricCard, Badge, FormGrid, InputGroup, ErreurMsg } from '../components/UI'

function MLInsights() {
  const { paireSelectionnee, setPaireSelectionnee } = usePair()

  const [tickerA, setTickerA]     = useState(paireSelectionnee.tickerA)
  const [tickerB, setTickerB]     = useState(paireSelectionnee.tickerB)
  const [dateDebut, setDateDebut] = useState(paireSelectionnee.dateDebut)
  const [dateFin, setDateFin]     = useState(paireSelectionnee.dateFin)
  const [chargement, setChargement] = useState(false)
  const [metriquesML, setMetriquesML] = useState(null)
  const [comparaison, setComparaison] = useState(null)
  const [erreur, setErreur]       = useState(null)

  useEffect(() => {
    setTickerA(paireSelectionnee.tickerA)
    setTickerB(paireSelectionnee.tickerB)
    setDateDebut(paireSelectionnee.dateDebut)
    setDateFin(paireSelectionnee.dateFin)
  }, [paireSelectionnee])

  const lancerAnalyse = async () => {
    setChargement(true)
    setErreur(null)
    setMetriquesML(null)
    setComparaison(null)
    setPaireSelectionnee({ ...paireSelectionnee, tickerA, tickerB, dateDebut, dateFin })
    try {
      const [repML, repComp] = await Promise.all([
        ApiService.obtenirMetriquesXGBoost(tickerA, tickerB, dateDebut, dateFin),
        ApiService.comparerStrategies(tickerA, tickerB, dateDebut, dateFin),
      ])
      setMetriquesML(repML.data)
      setComparaison(repComp.data)
    } catch {
      setErreur("Erreur lors de l'analyse ML. Vérifie que l'API est démarrée.")
    } finally {
      setChargement(false)
    }
  }

  const lignesComparaison = [
    { label: 'Rendement total',   key: 'rendement_total',  suffixe: ' %', drawdown: false },
    { label: 'Sharpe Ratio',      key: 'sharpe_ratio',     suffixe: '',   drawdown: false },
    { label: 'Max Drawdown',      key: 'max_drawdown',     suffixe: ' %', drawdown: true  },
    { label: 'Win Rate',          key: 'win_rate',         suffixe: ' %', drawdown: false },
    { label: 'Nombre de trades',  key: 'nombre_trades',    suffixe: '',   drawdown: false },
  ]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <PageTitle titre="ML Insights" sous="XGBoost · Comparaison classique vs ML-Enhanced" />

      <Card>
        <SectionTitle>Configuration</SectionTitle>
        <FormGrid cols={3}>
          <InputGroup label="Ticker A">
            <input type="text" value={tickerA} onChange={(e) => setTickerA(e.target.value.toUpperCase())} />
          </InputGroup>
          <InputGroup label="Ticker B">
            <input type="text" value={tickerB} onChange={(e) => setTickerB(e.target.value.toUpperCase())} />
          </InputGroup>
          <InputGroup label=" ">
            <Button onClick={lancerAnalyse} disabled={chargement} style={{ width: '100%' }}>
              {chargement ? 'Analyse en cours...' : "Lancer l'analyse ML →"}
            </Button>
          </InputGroup>
          <InputGroup label="Date début">
            <input type="date" value={dateDebut} onChange={(e) => setDateDebut(e.target.value)} />
          </InputGroup>
          <InputGroup label="Date fin">
            <input type="date" value={dateFin} onChange={(e) => setDateFin(e.target.value)} />
          </InputGroup>
        </FormGrid>
        <ErreurMsg message={erreur} />
      </Card>

      {metriquesML && (
        <Card>
          <SectionTitle>Métriques XGBoost</SectionTitle>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '10px' }}>
            <MetricCard label="Accuracy"  valeur={`${(metriquesML.accuracy  * 100).toFixed(1)} %`} couleur="green" />
            <MetricCard label="Precision" valeur={`${(metriquesML.precision * 100).toFixed(1)} %`} couleur="green" />
            <MetricCard label="Recall"    valeur={`${(metriquesML.recall    * 100).toFixed(1)} %`} couleur="green" />
            <MetricCard label="F1 Score"  valeur={`${(metriquesML.f1        * 100).toFixed(1)} %`} couleur="green" />
            <MetricCard label="ROC-AUC"   valeur={metriquesML.roc_auc.toFixed(3)}                  couleur="green" />
          </div>
        </Card>
      )}

      {comparaison && (
        <Card>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px', paddingBottom: '8px', borderBottom: '1px solid var(--border)' }}>
            <span style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '1px' }}>
              Comparaison Classique vs ML-Enhanced
            </span>
            <Badge variante={comparaison.amelioration_sharpe >= 0 ? 'green' : 'red'}>
              Sharpe {comparaison.amelioration_sharpe >= 0 ? '+' : ''}{comparaison.amelioration_sharpe}
            </Badge>
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
            <thead>
              <tr>
                {['Métrique', 'Classique', 'ML-Enhanced', 'Δ'].map((h, i) => (
                  <th key={h} style={{
                    textAlign: i === 0 ? 'left' : 'right',
                    fontSize: '9px', color: 'var(--text-muted)',
                    textTransform: 'uppercase', letterSpacing: '1px',
                    padding: '6px 0', borderBottom: '1px solid var(--border)', fontWeight: 500,
                  }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {lignesComparaison.map(({ label, key, suffixe, drawdown }) => {
                const delta     = (comparaison.ml_enhanced[key] - comparaison.classique[key]).toFixed(2)
                const positif   = parseFloat(delta) >= 0
                const ameliore  = drawdown ? !positif : positif
                return (
                  <tr key={key} style={{ borderBottom: '1px solid var(--bg-tertiary)' }}>
                    <td style={{ padding: '8px 0', color: 'var(--text-secondary)' }}>{label}</td>
                    <td style={{ padding: '8px 0', textAlign: 'right', color: 'var(--text-secondary)' }}>
                      {comparaison.classique[key]}{suffixe}
                    </td>
                    <td style={{ padding: '8px 0', textAlign: 'right', color: 'var(--text-primary)', fontWeight: 500 }}>
                      {comparaison.ml_enhanced[key]}{suffixe}
                    </td>
                    <td style={{
                      padding: '8px 0', textAlign: 'right', fontSize: '11px', fontWeight: 600,
                      color: ameliore ? 'var(--accent)' : 'var(--red)',
                    }}>
                      {positif ? '+' : ''}{delta}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </Card>
      )}
    </div>
  )
}

export default MLInsights
