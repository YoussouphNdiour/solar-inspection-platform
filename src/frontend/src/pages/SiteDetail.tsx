import { useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { InspectionList } from '../components/InspectionList'
import { useSiteStore, useMapStore } from '../store'

export const SiteDetail: React.FC = () => {
  const { siteId } = useParams<{ siteId: string }>()
  const { sites, selectSite } = useSiteStore()
  const { flyTo } = useMapStore()

  const site = sites.find((s) => s.id === siteId)

  useEffect(() => {
    if (siteId) selectSite(siteId)
    if (site) {
      flyTo(site.location.coordinates[1], site.location.coordinates[0], 14)
    }
  }, [siteId, site, selectSite, flyTo])

  if (!site) {
    return (
      <div className="p-6 text-gray-500">Site introuvable</div>
    )
  }

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold text-gray-900 mb-1">{site.name}</h1>
      <p className="text-sm text-gray-500 mb-6">
        {site.panel_count} panneaux · {site.surface_m2.toLocaleString()} m²
      </p>
      <InspectionList siteId={siteId} />
    </div>
  )
}
