import { useNavigate } from 'react-router-dom'
import { usePair } from '../context/PairContext'
import { Badge } from './UI'

function PairsList({ paires, dateDebut, dateFin }) {
  const navigate = useNavigate()
  const { setPaireSelectionnee } = usePair()

  if (!paires || paires.length === 0) {
    return (
      <p style={{ fontSize: '12px', color: 'var(--text-muted)', fontStyle: 'italic' }}>
        Aucune paire détectée.
      </p>
    )
  }

  const selectionnerPaire = (paire) => {
    setPaireSelectionnee({
      tickerA: paire.ticker_a,
      tickerB: paire.ticker_b,
      dateDebut: dateDebut || '2020-01-01',
      dateFin:   dateFin   || '2024-01-01',
      capital:   10000,
    })
    navigate('/backtest')
  }

  return (
    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
      <thead>
        <tr>
          {['Paire', 'Corrélation', 'P-valeur', 'Statut', ''].map((h) => (
            <th key={h} style={{
              textAlign: h === '' || h === 'Statut' ? 'center' : (h === 'Corrélation' || h === 'P-valeur' ? 'right' : 'left'),
              fontSize: '9px',
              color: 'var(--text-muted)',
              textTransform: 'uppercase',
              letterSpacing: '1px',
              padding: '6px 0',
              borderBottom: '1px solid var(--border)',
              fontWeight: 500,
            }}>
              {h}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {paires.map((paire) => (
          <tr
            key={`${paire.ticker_a}-${paire.ticker_b}`}
            style={{ borderBottom: '1px solid var(--bg-tertiary)' }}
          >
            <td style={{ padding: '9px 0', color: 'var(--text-primary)', fontWeight: 500 }}>
              {paire.ticker_a} / {paire.ticker_b}
            </td>
            <td style={{ padding: '9px 0', color: 'var(--text-secondary)', textAlign: 'right' }}>
              {paire.correlation.toFixed(3)}
            </td>
            <td style={{ padding: '9px 0', color: 'var(--text-secondary)', textAlign: 'right' }}>
              {paire.p_valeur.toFixed(4)}
            </td>
            <td style={{ padding: '9px 0', textAlign: 'center' }}>
              {paire.p_valeur < 0.05
                ? <Badge variante="green">cointégrée</Badge>
                : <Badge variante="amber">marginale</Badge>
              }
            </td>
            <td style={{ padding: '9px 0', textAlign: 'right' }}>
              <button
                onClick={() => selectionnerPaire(paire)}
                style={{
                  background: 'var(--accent-dim)',
                  color: 'var(--accent)',
                  border: '1px solid rgba(0,212,170,0.2)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '3px 10px',
                  fontSize: '10px',
                  fontWeight: 600,
                  fontFamily: 'var(--font-mono)',
                  cursor: 'pointer',
                  letterSpacing: '0.5px',
                }}
              >
                Analyser →
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export default PairsList
