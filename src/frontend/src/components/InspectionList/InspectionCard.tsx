import { format } from 'date-fns'
import { fr } from 'date-fns/locale'
import type { Inspection, InspectionStatus } from '../../types'

const STATUS_LABELS: Record<InspectionStatus, string> = {
  planned: 'Planifiée',
  in_progress: 'En cours',
  completed: 'Terminée',
  failed: 'Échouée',
}

const STATUS_COLORS: Record<InspectionStatus, string> = {
  planned: 'bg-blue-100 text-blue-800',
  in_progress: 'bg-yellow-100 text-yellow-800',
  completed: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
}

interface Props {
  inspection: Inspection
  onClick?: () => void
}

export const InspectionCard: React.FC<Props> = ({ inspection, onClick }) => {
  return (
    <div
      className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow cursor-pointer"
      onClick={onClick}
    >
      <div className="flex justify-between items-start">
        <div>
          <p className="text-xs text-gray-500 font-mono">
            #{inspection.id.slice(0, 8)}
          </p>
          <p className="mt-1 text-sm text-gray-700">
            {inspection.started_at
              ? format(new Date(inspection.started_at), 'dd MMM yyyy', { locale: fr })
              : format(new Date(inspection.created_at), 'dd MMM yyyy', { locale: fr })}
          </p>
        </div>
        <span className={`text-xs px-2 py-1 rounded-full font-medium ${STATUS_COLORS[inspection.status as InspectionStatus]}`}>
          {STATUS_LABELS[inspection.status as InspectionStatus]}
        </span>
      </div>

      {inspection.irradiance_wm2 && (
        <div className="mt-3 flex gap-3 text-xs text-gray-500">
          <span>☀️ {inspection.irradiance_wm2} W/m²</span>
          {inspection.wind_speed_ms && <span>💨 {inspection.wind_speed_ms} m/s</span>}
          {inspection.ambient_temp_c && <span>🌡 {inspection.ambient_temp_c}°C</span>}
        </div>
      )}
    </div>
  )
}
