import { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import Card from '../components/Card'
import Button from '../components/Button'
import ApiService from '../services/ApiService'
import { usePair } from '../context/PairContext'
import { PageTitle, SectionTitle, MetricCard, Badge, FormGrid, InputGroup, ErreurMsg } from '../components/UI'

const tooltipStyle = {
  backgroundColor: 'var(--bg-tertiary)',
  border: '1px solid var(--border)',
  borderRadius: '4px',
  fontFamily: 'var(--font-mono)',
  fontSize: '11px',
  color: 'var(--text-primary)',
}

function Performance() {
  const { paireSelectionnee, setPaireSelectionnee } = usePair()

  const [tickerA, setTickerA]     = useState(paireSelectionnee.tickerA)
  const [tickerB, setTickerB]     = useState(paireSelectionnee.tickerB)
  const [dateDebut, setDateDebut] = useState(paireSelectionnee.dateDebut)
  const [dateFin, setDateFin]     = useState(paireSelectionnee.dateFin)
  const [capital, setCapital]     = useState(paireSelectionnee.capital)
  const [chargement, setChargement] = useState(false)
  const [resultats, setResultats] = useState(null)
  const [erreur, setErreur]       = useState(null)

  useEffect(() => {
    setTickerA(paireSelectionnee.tickerA)
    setTickerB(paireSelectionnee.tickerB)
    setDateDebut(paireSelectionnee.dateDebut)
    setDateFin(paireSelectionnee.dateFin)
    setCapital(paireSelectionnee.capital)
  }, [paireSelectionnee])

  const lancerAnalyse = async () => {
    setChargement(true)
    setErreur(null)
    setResultats(null)
    setPaireSelectionnee({ tickerA, tickerB, dateDebut, dateFin, capital })
    try {
      const reponse = await ApiService.lancerBacktest(tickerA, tickerB, dateDebut, dateFin, capital)
      setResultats(reponse.data)
    } catch {
      setErreur("Erreur lors de l'analyse. Vérifie que l'API est démarrée.")
    } finally {
      setChargement(false)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <PageTitle titre="Performance" sous="Equity curve · Analyse des trades" />

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
            <Button onClick={lancerAnalyse} disabled={chargement} style={{ width: '100%' }}>
              {chargement ? 'Calcul...' : 'Analyser →'}
            </Button>
          </InputGroup>
        </FormGrid>
        <ErreurMsg message={erreur} />
      </Card>

      {resultats && (
        <>
          <Card>
            <SectionTitle>Equity Curve — {resultats.ticker_a} / {resultats.ticker_b}</SectionTitle>
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={resultats.equity_curve} margin={{ top: 4, right: 4, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="2 4" stroke="var(--border)" />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 10, fill: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}
                  axisLine={false} tickLine={false}
                  tickFormatter={(v) => v.slice(0, 7)}
                  interval={Math.floor(resultats.equity_curve.length / 6)}
                />
                <YAxis
                  tick={{ fontSize: 10, fill: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}
                  axisLine={false} tickLine={false}
                  tickFormatter={(v) => `${(v / 1000).toFixed(0)}k€`}
                />
                <Tooltip
                  contentStyle={tooltipStyle}
                  formatter={(v) => [`${v.toLocaleString('fr-FR')} €`, 'Capital']}
                  labelFormatter={(l) => `Date : ${l}`}
                />
                <Line type="monotone" dataKey="capital" stroke="var(--accent)" dot={false} strokeWidth={1.5} />
              </LineChart>
            </ResponsiveContainer>
          </Card>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px' }}>
            <MetricCard label="Rendement total" valeur={`${resultats.metriques.rendement_total} %`} couleur={resultats.metriques.rendement_total >= 0 ? 'green' : 'red'} />
            <MetricCard label="Sharpe Ratio"    valeur={resultats.metriques.sharpe_ratio} />
            <MetricCard label="Max Drawdown"    valeur={`${resultats.metriques.max_drawdown} %`} couleur="red" />
            <MetricCard label="Win Rate"        valeur={`${resultats.metriques.win_rate} %`} />
          </div>

          <Card>
            <SectionTitle>Trades ({resultats.trades.length})</SectionTitle>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
              <thead>
                <tr>
                  {['Date', 'Position', 'PnL (€)'].map((h, i) => (
                    <th key={h} style={{
                      textAlign: i === 2 ? 'right' : 'left',
                      fontSize: '9px', color: 'var(--text-muted)',
                      textTransform: 'uppercase', letterSpacing: '1px',
                      padding: '6px 0', borderBottom: '1px solid var(--border)', fontWeight: 500,
                    }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {resultats.trades.map((trade, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid var(--bg-tertiary)' }}>
                    <td style={{ padding: '8px 0', color: 'var(--text-secondary)' }}>{trade.date}</td>
                    <td style={{ padding: '8px 0' }}>
                      <Badge variante={trade.position === 1 ? 'green' : trade.position === -1 ? 'red' : 'gray'}>
                        {trade.position === 1 ? 'Long' : trade.position === -1 ? 'Short' : 'Neutre'}
                      </Badge>
                    </td>
                    <td style={{
                      padding: '8px 0', textAlign: 'right', fontWeight: 500,
                      color: trade.pnl >= 0 ? 'var(--accent)' : 'var(--red)',
                    }}>
                      {trade.pnl >= 0 ? '+' : ''}{trade.pnl}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </>
      )}
    </div>
  )
}

export default Performance
