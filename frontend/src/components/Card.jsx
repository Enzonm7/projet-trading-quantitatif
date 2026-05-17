function Card({ children, className = '', style = {} }) {
  return (
    <div
      className={className}
      style={{
        background: 'var(--bg-secondary)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-lg)',
        padding: '16px',
        ...style,
      }}
    >
      {children}
    </div>
  )
}

export default Card
