import { Link } from 'react-router-dom'

export const NotFound: React.FC = () => (
  <div className="flex flex-col items-center justify-center h-full gap-4">
    <p className="text-6xl">404</p>
    <p className="text-gray-500">Page introuvable</p>
    <Link to="/" className="text-yellow-600 hover:underline">
      Retour au tableau de bord
    </Link>
  </div>
)
