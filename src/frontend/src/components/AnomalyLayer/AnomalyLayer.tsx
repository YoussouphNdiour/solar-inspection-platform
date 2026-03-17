import { useCallback, useState } from 'react'
import { Layer, Popup, Source } from 'react-map-gl/maplibre'
import type { MapLayerMouseEvent } from 'maplibre-gl'
import type { AnomalyGeoJSON, AnomalyProperties, CoAClass } from '../../types'
import { AnomalyPopup } from './AnomalyPopup'

const COA_FILL_COLORS: Record<CoAClass, string> = {
  CoA1: '#FCD34D',
  CoA2: '#F97316',
  CoA3: '#EF4444',
}

interface Props {
  geojson: AnomalyGeoJSON
  visibleClasses?: CoAClass[]
}

export const AnomalyLayer: React.FC<Props> = ({
  geojson,
  visibleClasses = ['CoA1', 'CoA2', 'CoA3'],
}) => {
  const [selectedAnomaly, setSelectedAnomaly] = useState<{
    properties: AnomalyProperties
    longitude: number
    latitude: number
  } | null>(null)

  const filteredGeojson = {
    ...geojson,
    features: geojson.features.filter((f) =>
      visibleClasses.includes(f.properties.coa_class)
    ),
  }

  const handleClick = useCallback((event: MapLayerMouseEvent) => {
    if (!event.features?.length) return
    const feature = event.features[0]
    const coords = event.lngLat
    setSelectedAnomaly({
      properties: feature.properties as AnomalyProperties,
      longitude: coords.lng,
      latitude: coords.lat,
    })
  }, [])

  return (
    <>
      <Source id="anomalies" type="geojson" data={filteredGeojson as GeoJSON.FeatureCollection}>
        <Layer
          id="anomalies-fill"
          type="fill"
          paint={{
            'fill-color': [
              'match',
              ['get', 'coa_class'],
              'CoA1', COA_FILL_COLORS.CoA1,
              'CoA2', COA_FILL_COLORS.CoA2,
              'CoA3', COA_FILL_COLORS.CoA3,
              '#gray',
            ],
            'fill-opacity': 0.6,
          }}
          onClick={handleClick}
        />
        <Layer
          id="anomalies-outline"
          type="line"
          paint={{
            'line-color': '#ffffff',
            'line-width': 1,
          }}
        />
      </Source>

      {selectedAnomaly && (
        <Popup
          latitude={selectedAnomaly.latitude}
          longitude={selectedAnomaly.longitude}
          closeButton={false}
          anchor="bottom"
        >
          <AnomalyPopup
            properties={selectedAnomaly.properties}
            onClose={() => setSelectedAnomaly(null)}
          />
        </Popup>
      )}
    </>
  )
}
