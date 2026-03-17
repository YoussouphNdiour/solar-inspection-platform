import { useEffect } from 'react'
import { SiteMap } from '../components/SiteMap'
import { useSiteStore, useInspectionStore } from '../store'

export const Dashboard: React.FC = () => {
  const { sites, fetchSites } = useSiteStore()
  const { inspections, fetchInspections } = useInspectionStore()

  useEffect(() => {
    fetchSites()
    fetchInspections()
  }, [fetchSites, fetchInspections])

  const inProgressCount = inspections.filter((i) => i.status === 'processing').length
  const completedCount = inspections.filter((i) => i.status === 'report_ready').length

  return (
    <div className="h-full flex flex-col">
      {/* Statistiques */}
      <div className="p-4 grid grid-cols-3 gap-4 bg-white border-b">
        <StatCard label="Sites" value={sites.length} icon="📍" color="bg-blue-50" />
        <StatCard label="Inspections en cours" value={inProgressCount} icon="🔄" color="bg-yellow-50" />
        <StatCard label="Inspections terminées" value={completedCount} icon="✅" color="bg-green-50" />
      </div>

      {/* Carte */}
      <div className="flex-1">
        <SiteMap />
      </div>
    </div>
  )
}

interface StatCardProps {
  label: string
  value: number
  icon: string
  color: string
}

const StatCard: React.FC<StatCardProps> = ({ label, value, icon, color }) => (
  <div className={`${color} rounded-lg p-4 flex items-center gap-3`}>
    <span className="text-2xl">{icon}</span>
    <div>
      <p className="text-2xl font-bold text-gray-800">{value}</p>
      <p className="text-xs text-gray-600">{label}</p>
    </div>
  </div>
)
