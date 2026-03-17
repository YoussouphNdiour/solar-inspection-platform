import { NavLink } from 'react-router-dom'
import { clsx } from 'clsx'

const NAV_ITEMS = [
  { to: '/', label: 'Tableau de bord', icon: '🏠', end: true },
  { to: '/sites', label: 'Sites', icon: '📍', end: false },
  { to: '/sites/new', label: 'Nouvelle centrale', icon: '⚡', end: false },
  { to: '/inspections', label: 'Mes examens', icon: '🔍', end: true },
  { to: '/inspections/new', label: 'Nouvel examen', icon: '🔬', end: false },
  { to: '/upload', label: 'Upload photos', icon: '📤', end: false },
  { to: '/demo/malicounda', label: 'Démo Malicounda', icon: '☀️', end: false },
]

export const Sidebar: React.FC = () => {
  return (
    <nav className="w-56 bg-gray-900 text-white flex flex-col py-4">
      {NAV_ITEMS.map(({ to, label, icon, end }) => (
        <NavLink
          key={to}
          to={to}
          end={end}
          className={({ isActive }) =>
            clsx(
              'flex items-center gap-3 px-4 py-3 text-sm transition-colors',
              isActive
                ? 'bg-yellow-500 text-gray-900 font-semibold'
                : 'text-gray-300 hover:bg-gray-800 hover:text-white'
            )
          }
        >
          <span>{icon}</span>
          <span>{label}</span>
        </NavLink>
      ))}
    </nav>
  )
}
