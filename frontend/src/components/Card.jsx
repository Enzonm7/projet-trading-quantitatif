function Card({ children, className = '' }) {
  return (
    <div className={`bg-white rounded-lg border border-slate-200 p-4 ${className}`}>
      {children}
    </div>
  )
}

export default Card