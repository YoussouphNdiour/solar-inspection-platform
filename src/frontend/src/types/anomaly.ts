export type CoAClass = 'CoA1' | 'CoA2' | 'CoA3'

export type AnomalyType =
  | 'hotspot_cellule'
  | 'bypass_diode'
  | 'pid'
  | 'string_ouverte'
  | 'ombrage'
  | 'salissure'

export interface AnomalyProperties {
  panel_id: string
  delta_t_measured: number
  delta_t_normalized: number
  coa_class: CoAClass
  anomaly_type: AnomalyType
  confidence: number
  thermal_image_crop?: string
  rgb_image_crop?: string
}

export interface AnomalyFeature {
  type: 'Feature'
  geometry: {
    type: 'Polygon'
    coordinates: number[][][]
  }
  properties: AnomalyProperties
}

export interface AnomalyGeoJSON {
  type: 'FeatureCollection'
  inspection_id: string
  summary: {
    total_panels: number
    anomaly_count: number
    coa1: number
    coa2: number
    coa3: number
    estimated_power_loss_pct: number
  }
  features: AnomalyFeature[]
}
