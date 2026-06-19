import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import Card from '../components/Card'
import { PageTitle, SectionTitle, MetricCard, Badge } from '../components/UI'

const donneesEquity = [
  { date: 'Jan', capital: 10000 }, { date: 'Fév', capital: 10420 },
  { date: 'Mar', capital: 10150 }, { date: 'Avr', capital: 11200 },
  { date: 'Mai', capital: 11800 }, { date: 'Jun', capital: 11500 },
  { date: 'Jul', capital: 12400 }, { date: 'Aoû', capital: 12900 },
  { date: 'Sep', capital: 13100 }, { date: 'Oct', capital: 13800 },
  { date: 'Nov', capital: 14200 }, { date: 'Déc', capital: 13470 },
]

const pairesDemo = [
  { ticker_a: 'AAPL', ticker_b: 'MSFT', correlation: 0.923, p_valeur: 0.031 },
  { ticker_a: 'JPM',  ticker_b: 'BAC',  correlation: 0.881, p_valeur: 0.042 },
  { ticker_a: 'PEP',  ticker_b: 'KO',   correlation: 0.754, p_valeur: 0.098 },
]

const tooltipStyle = {
  backgroundColor: 'var(--bg-tertiary)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-sm)',
  fontFamily: 'var(--font-mono)',
  fontSize: '11px',
  color: 'var(--text-primary)',
}

function Dashboard() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <PageTitle titre="Dashboard" sous="Vue d'ensemble · Dernière analyse — données de démonstration" />

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px' }}>
        <MetricCard label="Sharpe Ratio"   valeur="1.84"  detail="↑ +0.42 vs classique" couleur="green" />
        <MetricCard label="Win Rate"       valeur="67.3%" detail="trades gagnants"                      />
        <MetricCard label="Max Drawdown"   valeur="-8.2%" detail="perte max observée"   couleur="red"   />
        <MetricCard label="Paires actives" valeur="4"     detail="sur 15 testées"                       />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        <Card>
          <SectionTitle>Equity Curve — AAPL / MSFT (démo)</SectionTitle>
          <ResponsiveContainer width="100%" height={160}>
            <LineChart data={donneesEquity} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
              <XAxis dataKey="date" tick={{ fontSize: 10, fill: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 10, fill: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }} axisLine={false} tickLine={false} tickFormatter={(v) => `${(v/1000).toFixed(0)}k`} />
              <Tooltip
                contentStyle={tooltipStyle}
                formatter={(v) => [`${v.toLocaleString('fr-FR')} €`, 'Capital']}
              />
              <Line type="monotone" dataKey="capital" stroke="var(--accent)" dot={false} strokeWidth={1.5} />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        <Card>
          <SectionTitle>Paires détectées (démo)</SectionTitle>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
            <thead>
              <tr>
                {['Paire', 'Corrél.', 'P-value', 'Statut'].map((h, i) => (
                  <th key={h} style={{
                    textAlign: i === 0 ? 'left' : 'right',
                    fontSize: '9px', color: 'var(--text-muted)',
                    textTransform: 'uppercase', letterSpacing: '1px',
                    padding: '4px 0', borderBottom: '1px solid var(--border)', fontWeight: 500,
                  }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {pairesDemo.map((p) => (
                <tr key={`${p.ticker_a}-${p.ticker_b}`} style={{ borderBottom: '1px solid var(--bg-tertiary)' }}>
                  <td style={{ padding: '8px 0', color: 'var(--text-primary)', fontWeight: 500 }}>{p.ticker_a} / {p.ticker_b}</td>
                  <td style={{ padding: '8px 0', color: 'var(--text-secondary)', textAlign: 'right' }}>{p.correlation.toFixed(3)}</td>
                  <td style={{ padding: '8px 0', color: 'var(--text-secondary)', textAlign: 'right' }}>{p.p_valeur.toFixed(3)}</td>
                  <td style={{ padding: '8px 0', textAlign: 'right' }}>
                    {p.p_valeur < 0.05
                      ? <Badge variante="green">cointégrée</Badge>
                      : <Badge variante="amber">marginale</Badge>
                    }
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <p style={{ fontSize: '9px', color: 'var(--text-muted)', marginTop: '10px' }}>
            Lance une vraie détection depuis <strong style={{ color: 'var(--accent)' }}>Exploration →</strong>
          </p>
        </Card>
      </div>
    </div>
  )
}

export default Dashboard
