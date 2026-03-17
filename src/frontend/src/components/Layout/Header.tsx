import { Link } from 'react-router-dom'

export const Header: React.FC = () => {
  return (
    <header className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
      <Link to="/" className="flex items-center gap-2">
        <span className="text-2xl">☀️</span>
        <span className="font-bold text-gray-800">Solar Inspection</span>
      </Link>
      <div className="text-sm text-gray-500">v0.1.0</div>
    </header>
  )
}
