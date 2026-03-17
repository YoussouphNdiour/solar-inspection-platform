import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import Map, { NavigationControl } from 'react-map-gl/maplibre'
import 'maplibre-gl/dist/maplibre-gl.css'
import { AnomalyLayer } from '../components/AnomalyLayer'
import { useInspectionStore, useMapStore } from '../store'
import { inspectionsApi } from '../api/inspections'
import type { AnomalyGeoJSON, CoAClass } from '../types'

export const InspectionDetail: React.FC = () => {
  const { inspectionId } = useParams<{ inspectionId: string }>()
  const { fetchInspections } = useInspectionStore()
  const { viewport, setViewport } = useMapStore()
  const [anomalies, setAnomalies] = useState<AnomalyGeoJSON | null>(null)
  const [coaFilter, setCoaFilter] = useState<CoAClass[]>(['CoA1', 'CoA2', 'CoA3'])

  useEffect(() => {
    fetchInspections()
  }, [fetchInspections])

  useEffect(() => {
    if (!inspectionId) return
    inspectionsApi
      .getAnomalies(inspectionId)
      .then(setAnomalies)
      .catch(() => setAnomalies(null))
  }, [inspectionId])

  return (
    <div className="h-full flex">
      {/* Panneau latéral */}
      <div className="w-72 p-4 bg-white border-r overflow-auto">
        <h1 className="font-bold text-gray-900 mb-1">Inspection</h1>
        <p className="text-xs font-mono text-gray-400 mb-4">#{inspectionId?.slice(0, 8)}</p>

        {anomalies && (
          <>
            <div className="space-y-2 mb-4">
              {(['CoA1', 'CoA2', 'CoA3'] as CoAClass[]).map((coa) => {
                const count = anomalies.summary[coa.toLowerCase() as 'coa1' | 'coa2' | 'coa3']
                const colors: Record<CoAClass, string> = {
                  CoA1: 'bg-yellow-100 border-yellow-300 text-yellow-800',
                  CoA2: 'bg-orange-100 border-orange-300 text-orange-800',
                  CoA3: 'bg-red-100 border-red-300 text-red-800',
                }
                return (
                  <label key={coa} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={coaFilter.includes(coa)}
                      onChange={(e) =>
                        setCoaFilter((prev) =>
                          e.target.checked ? [...prev, coa] : prev.filter((c) => c !== coa)
                        )
                      }
                    />
                    <span className={`text-xs px-2 py-0.5 rounded border font-medium ${colors[coa]}`}>
                      {coa}
                    </span>
                    <span className="text-sm text-gray-600">{count}</span>
                  </label>
                )
              })}
            </div>

            <p className="text-xs text-gray-500">
              Perte estimée :{' '}
              <span className="font-semibold text-gray-700">
                {anomalies.summary.estimated_power_loss_pct.toFixed(1)}%
              </span>
            </p>
          </>
        )}
      </div>

      {/* Carte */}
      <div className="flex-1">
        <Map
          mapStyle="https://demotiles.maplibre.org/style.json"
          {...viewport}
          onMove={(evt) => setViewport(evt.viewState)}
          style={{ width: '100%', height: '100%' }}
          interactiveLayerIds={['anomalies-fill']}
        >
          <NavigationControl position="top-right" />
          {anomalies && <AnomalyLayer geojson={anomalies} visibleClasses={coaFilter} />}
        </Map>
      </div>
    </div>
  )
}
