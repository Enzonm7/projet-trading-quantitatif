const variantes = {
  primary: 'bg-blue-600 text-white hover:bg-blue-700',
  secondary: 'bg-slate-100 text-slate-700 hover:bg-slate-200',
  danger: 'bg-red-600 text-white hover:bg-red-700',
}

function Button({ children, onClick, variante = 'primary', disabled = false, className = '' }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        px-4 py-2 rounded-md text-sm font-medium transition-colors
        disabled:opacity-50 disabled:cursor-not-allowed
        ${variantes[variante]} ${className}
      `}
    >
      {children}
    </button>
  )
}

export default Button