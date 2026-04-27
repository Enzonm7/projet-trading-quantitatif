function PairsList({ paires }) {
  if (paires.length === 0) {
    return (
      <p className="text-sm text-slate-400 italic">Aucune paire détectée.</p>
    )
  }

  return (
    <table className="w-full text-sm">
      <thead>
        <tr className="border-b border-slate-200">
          <th className="text-left text-xs text-slate-500 font-medium pb-2">Paire</th>
          <th className="text-left text-xs text-slate-500 font-medium pb-2">Corrélation</th>
          <th className="text-left text-xs text-slate-500 font-medium pb-2">P-valeur</th>
          <th className="text-left text-xs text-slate-500 font-medium pb-2">Statut</th>
        </tr>
      </thead>
      <tbody>
        {paires.map((paire) => (
          <tr key={`${paire.ticker_a}-${paire.ticker_b}`} className="border-b border-slate-100 hover:bg-slate-50">
            <td className="py-2 font-medium text-slate-700">
              {paire.ticker_a} / {paire.ticker_b}
            </td>
            <td className="py-2 text-slate-600">
              {paire.correlation.toFixed(3)}
            </td>
            <td className="py-2 text-slate-600">
              {paire.p_valeur.toFixed(4)}
            </td>
            <td className="py-2">
              {paire.p_valeur < 0.05 ? (
                <span className="bg-green-100 text-green-700 text-xs px-2 py-0.5 rounded-full">
                  cointégrée
                </span>
              ) : (
                <span className="bg-amber-100 text-amber-700 text-xs px-2 py-0.5 rounded-full">
                  marginale
                </span>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export default PairsList