import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { InspectionCard } from './InspectionCard'
import { useInspectionStore } from '../../store'
import type { InspectionStatus } from '../../types'

const STATUS_OPTIONS: Array<{ value: InspectionStatus | ''; label: string }> = [
  { value: '', label: 'Tous les statuts' },
  { value: 'planned', label: 'Planifiées' },
  { value: 'in_progress', label: 'En cours' },
  { value: 'completed', label: 'Terminées' },
  { value: 'failed', label: 'Échouées' },
]

interface Props {
  siteId?: string
}

export const InspectionList: React.FC<Props> = ({ siteId }) => {
  const { inspections, isLoading, error, fetchInspections } = useInspectionStore()
  const [statusFilter, setStatusFilter] = useState<InspectionStatus | ''>('')
  const navigate = useNavigate()

  useEffect(() => {
    fetchInspections(siteId, statusFilter || undefined)
  }, [siteId, statusFilter, fetchInspections])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-32">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-yellow-500" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm">
        {error}
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <div className="flex justify-between items-center">
        <h2 className="font-semibold text-gray-800">
          Inspections ({inspections.length})
        </h2>
        <select
          className="text-sm border border-gray-300 rounded-md px-2 py-1"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as InspectionStatus | '')}
        >
          {STATUS_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      {inspections.length === 0 ? (
        <p className="text-gray-500 text-sm text-center py-8">Aucune inspection trouvée</p>
      ) : (
        inspections.map((inspection) => (
          <InspectionCard
            key={inspection.id}
            inspection={inspection}
            onClick={() => navigate(`/inspections/${inspection.id}`)}
          />
        ))
      )}
    </div>
  )
}
