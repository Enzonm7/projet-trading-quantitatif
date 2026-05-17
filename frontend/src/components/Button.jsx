const variantes = {
  primary: {
    background: 'var(--accent)',
    color: '#0a0b0f',
    border: 'none',
  },
  secondary: {
    background: 'transparent',
    color: 'var(--text-secondary)',
    border: '1px solid var(--border)',
  },
  danger: {
    background: 'var(--red-dim)',
    color: 'var(--red)',
    border: '1px solid var(--red)',
  },
}

function Button({ children, onClick, variante = 'primary', disabled = false, className = '', style = {} }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={className}
      style={{
        ...variantes[variante],
        padding: '8px 16px',
        borderRadius: 'var(--radius-sm)',
        fontSize: '11px',
        fontWeight: 600,
        fontFamily: 'var(--font-mono)',
        cursor: disabled ? 'not-allowed' : 'pointer',
        opacity: disabled ? 0.5 : 1,
        transition: 'opacity 0.15s',
        whiteSpace: 'nowrap',
        ...style,
      }}
    >
      {children}
    </button>
  )
}

export default Button
