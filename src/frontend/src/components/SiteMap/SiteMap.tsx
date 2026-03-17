import { useEffect, useState } from 'react'
import Map, { Marker, NavigationControl, Popup } from 'react-map-gl/maplibre'
import 'maplibre-gl/dist/maplibre-gl.css'
import { useSiteStore, useMapStore } from '../../store'
import type { Site } from '../../types'

export const SiteMap: React.FC = () => {
  const { sites, selectedSiteId, fetchSites, selectSite } = useSiteStore()
  const { viewport, setViewport } = useMapStore()
  const [hoveredSite, setHoveredSite] = useState<Site | null>(null)

  useEffect(() => {
    fetchSites()
  }, [fetchSites])

  return (
    <Map
      mapStyle="https://demotiles.maplibre.org/style.json"
      latitude={viewport.latitude}
      longitude={viewport.longitude}
      zoom={viewport.zoom}
      onMove={(evt) => setViewport(evt.viewState)}
      style={{ width: '100%', height: '100%' }}
    >
      <NavigationControl position="top-right" />

      {sites.map((site) => (
        <Marker
          key={site.id}
          latitude={site.location.coordinates[1]}
          longitude={site.location.coordinates[0]}
          onClick={() => selectSite(site.id)}
        >
          <button
            className={`w-6 h-6 rounded-full border-2 border-white shadow-md transition-transform hover:scale-125 ${
              selectedSiteId === site.id
                ? 'bg-solar-500 scale-125'
                : 'bg-yellow-400'
            }`}
            onMouseEnter={() => setHoveredSite(site)}
            onMouseLeave={() => setHoveredSite(null)}
            aria-label={`Site : ${site.name}`}
          />
        </Marker>
      ))}

      {hoveredSite && (
        <Popup
          latitude={hoveredSite.location.coordinates[1]}
          longitude={hoveredSite.location.coordinates[0]}
          closeButton={false}
          offset={20}
        >
          <div className="text-sm">
            <p className="font-semibold">{hoveredSite.name}</p>
            <p className="text-gray-600">{hoveredSite.panel_count} panneaux</p>
            <p className="text-gray-600">{hoveredSite.surface_m2.toLocaleString()} m²</p>
          </div>
        </Popup>
      )}
    </Map>
  )
}
