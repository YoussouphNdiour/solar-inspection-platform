export interface GeoJSONPoint {
  type: 'Point'
  coordinates: [number, number] // [longitude, latitude]
}

export interface Site {
  id: string
  name: string
  location: GeoJSONPoint
  surface_m2: number
  panel_count: number
  created_at: string
}

export interface SiteCreate {
  name: string
  location: GeoJSONPoint
  surface_m2: number
  panel_count: number
}
