import { useEffect, useState } from 'react'
import ApiService from '../services/ApiService'

function Header() {
  const [heure, setHeure] = useState('')
  const [apiOk, setApiOk] = useState(null)

  useEffect(() => {
    const maj = () => {
      const now = new Date()
      setHeure(now.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' }))
    }
    maj()
    const id = setInterval(maj, 1000)
    return () => clearInterval(id)
  }, [])

  useEffect(() => {
    ApiService.verifierSante()
      .then(() => setApiOk(true))
      .catch(() => setApiOk(false))
  }, [])

  return (
    <header style={{
      height: '48px',
      background: 'var(--bg-secondary)',
      borderBottom: '1px solid var(--border)',
      display: 'flex',
      alignItems: 'center',
      padding: '0 20px',
      gap: '16px',
      flexShrink: 0,
    }}>
      <span style={{
        fontFamily: 'var(--font-display)',
        fontWeight: 700,
        fontSize: '16px',
        letterSpacing: '0.5px',
        color: 'var(--accent)',
      }}>
        Pair<span style={{ color: 'var(--text-primary)' }}>Lens</span>
      </span>

      <span style={{ color: 'var(--border)', fontSize: '16px' }}>|</span>

      <span style={{ color: 'var(--text-muted)', fontSize: '10px', textTransform: 'uppercase', letterSpacing: '1px' }}>
        ML-Enhanced Pairs Trading
      </span>

      <div style={{ flex: 1 }} />

      {apiOk !== null && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{
            width: '6px', height: '6px', borderRadius: '50%',
            background: apiOk ? 'var(--accent)' : 'var(--red)',
            boxShadow: apiOk ? '0 0 6px var(--accent)' : '0 0 6px var(--red)',
            animation: 'pulse 2s ease-in-out infinite',
          }} />
          <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
            {apiOk ? 'API connectée' : 'API hors ligne'}
          </span>
        </div>
      )}

      <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontVariantNumeric: 'tabular-nums' }}>
        {heure}
      </span>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.4; }
        }
      `}</style>
    </header>
  )
}

export default Header
