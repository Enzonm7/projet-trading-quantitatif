// PageTitle
export function PageTitle({ titre, sous }) {
  return (
    <div style={{ marginBottom: '20px' }}>
      <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '20px', fontWeight: 600, color: 'var(--text-primary)', letterSpacing: '-0.3px' }}>
        {titre}
      </h2>
      {sous && (
        <p style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '1px', marginTop: '2px' }}>
          {sous}
        </p>
      )}
    </div>
  )
}

// SectionTitle
export function SectionTitle({ children }) {
  return (
    <p style={{
      fontSize: '10px',
      color: 'var(--text-muted)',
      textTransform: 'uppercase',
      letterSpacing: '1px',
      marginBottom: '12px',
      paddingBottom: '8px',
      borderBottom: '1px solid var(--border)',
    }}>
      {children}
    </p>
  )
}

// MetricCard
export function MetricCard({ label, valeur, detail, couleur }) {
  const couleurs = {
    green: 'var(--accent)',
    red: 'var(--red)',
    amber: 'var(--amber)',
    default: 'var(--text-primary)',
  }
  return (
    <div style={{
      background: 'var(--bg-tertiary)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--radius-md)',
      padding: '14px',
    }}>
      <p style={{ fontSize: '9px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '6px' }}>
        {label}
      </p>
      <p style={{ fontSize: '22px', fontWeight: 600, color: couleurs[couleur] || couleurs.default, lineHeight: 1 }}>
        {valeur}
      </p>
      {detail && (
        <p style={{ fontSize: '9px', color: 'var(--text-muted)', marginTop: '4px' }}>
          {detail}
        </p>
      )}
    </div>
  )
}

// Badge
export function Badge({ children, variante = 'green' }) {
  const styles = {
    green: { background: 'var(--accent-dim)', color: 'var(--accent)' },
    red:   { background: 'var(--red-dim)',   color: 'var(--red)'    },
    amber: { background: 'var(--amber-dim)', color: 'var(--amber)'  },
    gray:  { background: 'rgba(255,255,255,0.06)', color: 'var(--text-secondary)' },
  }
  return (
    <span style={{
      ...styles[variante],
      fontSize: '9px',
      fontWeight: 600,
      padding: '3px 8px',
      borderRadius: 'var(--radius-sm)',
      letterSpacing: '0.5px',
    }}>
      {children}
    </span>
  )
}

// FormGrid
export function FormGrid({ children, cols = 3 }) {
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: `repeat(${cols}, 1fr)`,
      gap: '12px',
      marginBottom: '12px',
    }}>
      {children}
    </div>
  )
}

// InputGroup
export function InputGroup({ label, children, span }) {
  return (
    <div style={{ gridColumn: span ? `span ${span}` : undefined }}>
      <label style={{
        display: 'block',
        fontSize: '9px',
        color: 'var(--text-muted)',
        textTransform: 'uppercase',
        letterSpacing: '1px',
        marginBottom: '5px',
      }}>
        {label}
      </label>
      {children}
    </div>
  )
}

// Erreur
export function ErreurMsg({ message }) {
  if (!message) return null
  return (
    <p style={{ fontSize: '11px', color: 'var(--red)', marginTop: '8px', padding: '8px 10px', background: 'var(--red-dim)', borderRadius: 'var(--radius-sm)' }}>
      {message}
    </p>
  )
}
