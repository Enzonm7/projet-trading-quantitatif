import { NavLink } from 'react-router-dom'

const icones = {
  dashboard: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/>
      <rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>
    </svg>
  ),
  exploration: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
    </svg>
  ),
  backtest: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
    </svg>
  ),
  performance: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>
    </svg>
  ),
  ml: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 2a4 4 0 0 1 4 4c0 1.5-.8 2.8-2 3.5V12h2a2 2 0 0 1 2 2v1a2 2 0 0 1-2 2h-2v1.5c1.2.7 2 2 2 3.5a4 4 0 0 1-8 0c0-1.5.8-2.8 2-3.5V16H8a2 2 0 0 1-2-2v-1a2 2 0 0 1 2-2h2V9.5C8.8 8.8 8 7.5 8 6a4 4 0 0 1 4-4z"/>
    </svg>
  ),
}

const liens = [
  { chemin: '/',            label: 'Dashboard',   icone: icones.dashboard   },
  { chemin: '/exploration', label: 'Exploration', icone: icones.exploration },
  { chemin: '/backtest',    label: 'Backtest',    icone: icones.backtest    },
  { chemin: '/performance', label: 'Performance', icone: icones.performance },
  { chemin: '/ml-insights', label: 'ML Insights', icone: icones.ml         },
]

const styleBase = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  gap: '2px',
  padding: '8px 0',
  cursor: 'pointer',
  textDecoration: 'none',
  color: 'var(--text-muted)',
  transition: 'color 0.15s',
  width: '100%',
  position: 'relative',
}

function NavItem({ lien }) {
  return (
    <NavLink
      to={lien.chemin}
      end={lien.chemin === '/'}
      style={({ isActive }) => ({
        ...styleBase,
        color: isActive ? 'var(--accent)' : 'var(--text-muted)',
        background: isActive ? 'var(--accent-glow)' : 'transparent',
      })}
    >
      {({ isActive }) => (
        <>
          {isActive && (
            <span style={{
              position: 'absolute',
              left: 0,
              top: '50%',
              transform: 'translateY(-50%)',
              width: '2px',
              height: '24px',
              background: 'var(--accent)',
              borderRadius: '0 2px 2px 0',
            }} />
          )}
          <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            {lien.icone}
          </span>
          <span style={{
            fontSize: '9px',
            letterSpacing: '0.5px',
            textTransform: 'uppercase',
            lineHeight: 1,
            color: isActive ? 'var(--accent)' : 'var(--text-muted)',
          }}>
            {lien.label === 'ML Insights' ? 'ML' : lien.label.slice(0, 5)}
          </span>
        </>
      )}
    </NavLink>
  )
}

function Sidebar() {
  return (
    <aside style={{
      width: '56px',
      background: 'var(--bg-secondary)',
      borderRight: '1px solid var(--border)',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      paddingTop: '12px',
      gap: '4px',
      flexShrink: 0,
    }}>
      {liens.map((lien) => (
        <NavItem key={lien.chemin} lien={lien} />
      ))}
    </aside>
  )
}

export default Sidebar
