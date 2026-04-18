import { NavLink } from 'react-router-dom'

const liens = [
  { chemin: '/',              label: 'Dashboard' },
  { chemin: '/exploration',   label: 'Exploration' },
  { chemin: '/backtest',      label: 'Backtest' },
  { chemin: '/performance',   label: 'Performance' },
  { chemin: '/ml-insights',   label: 'ML Insights' },
]

function Sidebar() {
  return (
    <aside className="w-48 bg-slate-800 text-slate-200 flex flex-col py-4">
      {liens.map((lien) => (
        <NavLink
          key={lien.chemin}
          to={lien.chemin}
          end={lien.chemin === '/'}
          className={({ isActive }) =>
            `px-6 py-3 text-sm font-medium hover:bg-slate-700 transition-colors ${
              isActive ? 'bg-slate-700 text-white border-l-4 border-blue-400' : ''
            }`
          }
        >
          {lien.label}
        </NavLink>
      ))}
    </aside>
  )
}

export default Sidebar