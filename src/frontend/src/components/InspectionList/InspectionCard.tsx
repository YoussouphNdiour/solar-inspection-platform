import { format } from 'date-fns'
import { fr } from 'date-fns/locale'
import type { InspectionResponse, InspectionStatus } from '../../types/inspection'

const STATUS_LABELS: Record<InspectionStatus, string> = {
  created: 'Créée',
  images_uploaded: 'Images reçues',
  processing: 'Traitement',
  analysis_done: 'Analyse terminée',
  report_ready: 'Rapport prêt',
}

const STATUS_COLORS: Record<InspectionStatus, string> = {
  created: 'bg-gray-100 text-gray-800',
  images_uploaded: 'bg-blue-100 text-blue-800',
  processing: 'bg-yellow-100 text-yellow-800',
  analysis_done: 'bg-purple-100 text-purple-800',
  report_ready: 'bg-green-100 text-green-800',
}

interface Props {
  inspection: InspectionResponse
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
          <p className="text-xs text-gray-500 font-mono">#{inspection.id.slice(0, 8)}</p>
          <p className="mt-1 text-sm text-gray-700">
            {format(new Date(inspection.created_at), 'dd MMM yyyy', { locale: fr })}
          </p>
          {inspection.site_name && (
            <p className="text-xs text-gray-500 mt-0.5">{inspection.site_name}</p>
          )}
        </div>
        <span
          className={`text-xs px-2 py-1 rounded-full font-medium ${STATUS_COLORS[inspection.status]}`}
        >
          {STATUS_LABELS[inspection.status]}
        </span>
      </div>

      <div className="mt-3 flex gap-3 text-xs text-gray-500">
        <span>
          {inspection.plan_type === 'professional_5gsd' ? 'Pro 5 GSD' : 'Enterprise 3 GSD'}
        </span>
        <span>• ${inspection.total_amount_usd?.toFixed(2)}</span>
      </div>
    </div>
  )
}
