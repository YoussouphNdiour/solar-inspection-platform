import { useCallback, useEffect, useState } from 'react'
import Map, { Layer, NavigationControl, Popup, Source } from 'react-map-gl/maplibre'
import 'maplibre-gl/dist/maplibre-gl.css'
import type { MapLayerMouseEvent } from 'maplibre-gl'
import type { AnomalyProperties, CoAClass } from '../types'
import { AnomalyPopup } from '../components/AnomalyLayer/AnomalyPopup'

// ── Types ─────────────────────────────────────────────────────────────────────

interface GeoJSONData {
  type: 'FeatureCollection'
  site_name: string
  acquisition_date: string
  conditions: {
    irradiance_wm2: number
    normalization_factor: number
    ambient_temp_c: number
    wind_speed_ms: number
  }
  summary: {
    total_panels_analyzed: number
    anomaly_count: number
    coa1: number
    coa2: number
    coa3: number
    estimated_power_loss_pct: number
  }
  features: GeoJSON.Feature[]
}

const COA_COLORS: Record<CoAClass, string> = {
  CoA1: '#FCD34D',
  CoA2: '#F97316',
  CoA3: '#EF4444',
}

const COA_BADGE: Record<CoAClass, string> = {
  CoA1: 'bg-yellow-100 border-yellow-300 text-yellow-800',
  CoA2: 'bg-orange-100 border-orange-300 text-orange-800',
  CoA3: 'bg-red-100 border-red-300 text-red-800',
}

// ── Page ──────────────────────────────────────────────────────────────────────

export const MalicoundaDemo: React.FC = () => {
  const [data, setData] = useState<GeoJSONData | null>(null)
  const [coaFilter, setCoaFilter] = useState<CoAClass[]>(['CoA1', 'CoA2', 'CoA3'])
  const [selectedAnomaly, setSelectedAnomaly] = useState<{
    properties: AnomalyProperties
    longitude: number
    latitude: number
  } | null>(null)
  const [viewport, setViewport] = useState({
    latitude: 14.663,
    longitude: -16.931,
    zoom: 14.5,
  })

  useEffect(() => {
    fetch('/demo/malicounda.geojson')
      .then((r) => r.json())
      .then(setData)
      .catch(console.error)
  }, [])

  const filteredGeojson = data
    ? {
        type: 'FeatureCollection' as const,
        features: data.features.filter((f) =>
          coaFilter.includes((f.properties as AnomalyProperties).coa_class)
        ),
      }
    : null

  const handleClick = useCallback((e: MapLayerMouseEvent) => {
    if (!e.features?.length) return
    setSelectedAnomaly({
      properties: e.features[0].properties as AnomalyProperties,
      longitude: e.lngLat.lng,
      latitude: e.lngLat.lat,
    })
  }, [])

  const toggleCoa = (coa: CoAClass, checked: boolean) =>
    setCoaFilter((prev) => (checked ? [...prev, coa] : prev.filter((c) => c !== coa)))

  return (
    <div className="h-full flex">
      {/* ── Panneau latéral ──────────────────────────────────────────────── */}
      <aside className="w-72 bg-white border-r flex flex-col overflow-y-auto">
        {/* En-tête */}
        <div className="p-4 bg-gray-900 text-white">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-lg">☀️</span>
            <h1 className="font-bold text-base">Centrale Malicounda</h1>
          </div>
          <p className="text-xs text-gray-400">Sénégal · Inspection drone DJI Mavic 3T</p>
          {data && (
            <p className="text-xs text-gray-400 mt-0.5">
              {new Date(data.acquisition_date).toLocaleDateString('fr-FR', {
                day: 'numeric',
                month: 'long',
                year: 'numeric',
              })}
            </p>
          )}
        </div>

        {/* Statistiques */}
        {data && (
          <div className="p-4 border-b">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">
              Résultats IEC 62446-3
            </p>
            <div className="grid grid-cols-2 gap-2 mb-3">
              <StatBox label="Panneaux analysés" value={data.summary.total_panels_analyzed.toLocaleString()} />
              <StatBox label="Anomalies détectées" value={data.summary.anomaly_count} highlight />
              <StatBox label="Perte puissance" value={`${data.summary.estimated_power_loss_pct}%`} />
              <StatBox label="Irradiance" value={`${data.conditions.irradiance_wm2} W/m²`} />
            </div>

            {/* CoA par classe */}
            <div className="space-y-1.5">
              {(['CoA3', 'CoA2', 'CoA1'] as CoAClass[]).map((coa) => {
                const count = data.summary[coa.toLowerCase() as 'coa1' | 'coa2' | 'coa3']
                const pct = Math.round((count / data.summary.anomaly_count) * 100)
                return (
                  <label key={coa} className="flex items-center gap-2 cursor-pointer group">
                    <input
                      type="checkbox"
                      checked={coaFilter.includes(coa)}
                      onChange={(e) => toggleCoa(coa, e.target.checked)}
                      className="accent-gray-700"
                    />
                    <span
                      className={`text-xs px-2 py-0.5 rounded border font-semibold ${COA_BADGE[coa]}`}
                    >
                      {coa}
                    </span>
                    <div className="flex-1">
                      <div className="flex justify-between text-xs text-gray-600 mb-0.5">
                        <span>{count} anomalies</span>
                        <span>{pct}%</span>
                      </div>
                      <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className="h-full rounded-full"
                          style={{
                            width: `${pct}%`,
                            backgroundColor: COA_COLORS[coa],
                          }}
                        />
                      </div>
                    </div>
                  </label>
                )
              })}
            </div>
          </div>
        )}

        {/* Conditions de mesure */}
        {data && (
          <div className="p-4 border-b">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
              Conditions
            </p>
            <div className="space-y-1 text-xs text-gray-600">
              <Row label="Irradiance" value={`${data.conditions.irradiance_wm2} W/m²`} />
              <Row label="Température ambiante" value={`${data.conditions.ambient_temp_c}°C`} />
              <Row label="Vitesse vent" value={`${data.conditions.wind_speed_ms} m/s`} />
              <Row label="Facteur normalisation" value={`×${data.conditions.normalization_factor}`} />
            </div>
          </div>
        )}

        {/* Légende */}
        <div className="p-4">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Légende</p>
          <div className="space-y-1.5 text-xs text-gray-600">
            <LegendRow color={COA_COLORS.CoA1} label="CoA1 — ΔT < 10°C (Attention)" />
            <LegendRow color={COA_COLORS.CoA2} label="CoA2 — ΔT 10-40°C (Critique)" />
            <LegendRow color={COA_COLORS.CoA3} label="CoA3 — ΔT ≥ 40°C (Urgent)" />
          </div>
          <p className="text-xs text-gray-400 mt-3">
            Cliquer sur un panneau pour voir les détails.
          </p>
        </div>
      </aside>

      {/* ── Carte ──────────────────────────────────────────────────────────── */}
      <div className="flex-1 relative">
        {!data && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-50 z-10">
            <p className="text-gray-400 text-sm">Chargement des données…</p>
          </div>
        )}
        <Map
          mapStyle="https://demotiles.maplibre.org/style.json"
          latitude={viewport.latitude}
          longitude={viewport.longitude}
          zoom={viewport.zoom}
          onMove={(evt) => setViewport(evt.viewState)}
          style={{ width: '100%', height: '100%' }}
          interactiveLayerIds={['anomalies-fill']}
          onClick={handleClick}
        >
          <NavigationControl position="top-right" />

          {filteredGeojson && (
            <Source id="anomalies" type="geojson" data={filteredGeojson}>
              <Layer
                id="anomalies-fill"
                type="fill"
                paint={{
                  'fill-color': [
                    'match',
                    ['get', 'coa_class'],
                    'CoA1', COA_COLORS.CoA1,
                    'CoA2', COA_COLORS.CoA2,
                    'CoA3', COA_COLORS.CoA3,
                    '#888888',
                  ],
                  'fill-opacity': 0.75,
                }}
              />
              <Layer
                id="anomalies-outline"
                type="line"
                paint={{ 'line-color': '#ffffff', 'line-width': 1.5 }}
              />
            </Source>
          )}

          {selectedAnomaly && (
            <Popup
              latitude={selectedAnomaly.latitude}
              longitude={selectedAnomaly.longitude}
              closeButton={false}
              anchor="bottom"
              maxWidth="280px"
            >
              <AnomalyPopup
                properties={selectedAnomaly.properties}
                onClose={() => setSelectedAnomaly(null)}
              />
            </Popup>
          )}
        </Map>
      </div>
    </div>
  )
}

// ── Helpers ───────────────────────────────────────────────────────────────────

const StatBox: React.FC<{ label: string; value: string | number; highlight?: boolean }> = ({
  label,
  value,
  highlight,
}) => (
  <div className={`rounded p-2 text-center ${highlight ? 'bg-red-50' : 'bg-gray-50'}`}>
    <p className={`text-lg font-bold ${highlight ? 'text-red-600' : 'text-gray-800'}`}>{value}</p>
    <p className="text-xs text-gray-500 leading-tight">{label}</p>
  </div>
)

const Row: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <div className="flex justify-between">
    <span>{label}</span>
    <span className="font-mono font-medium text-gray-800">{value}</span>
  </div>
)

const LegendRow: React.FC<{ color: string; label: string }> = ({ color, label }) => (
  <div className="flex items-center gap-2">
    <span className="w-3 h-3 rounded-sm flex-shrink-0" style={{ backgroundColor: color }} />
    <span>{label}</span>
  </div>
)
