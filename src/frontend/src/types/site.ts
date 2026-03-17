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

export type SiteType = 'ground' | 'rooftop' | 'residential' | 'floating'
export type MountingType = 'fixed' | 'tracker_single_axis' | 'tracker_dual_axis'
export type AzimuthDirection = 'N' | 'NE' | 'E' | 'SE' | 'S' | 'SW' | 'W' | 'NW'
export type PowerUnit = 'kW' | 'MW'
export type PanelType = 'mono' | 'poly' | 'bifacial' | 'thin_film'
export type BosComponentType = 'inverter' | 'combiner_box' | 'cable' | 'mounting' | 'monitoring'

export interface SiteFormData {
  // Étape 1
  site_type: SiteType
  name: string
  installation_date: string
  mounting_type: MountingType
  tilt_angle_deg: number
  azimuth_direction: AzimuthDirection
  azimuth_degrees: number
  dc_power_installed_kw: number
  dc_power_unit: PowerUnit
  energy_sale_price: number
  currency: string
  address_line1: string
  address_line2?: string
  district: string
  city: string
  state_province?: string
  country: string
  postal_code: string
  latitude: number
  longitude: number
  kml_file?: File
  // Étape 2
  panels: PanelModuleForm[]
  // Étape 3
  bos_components: BosComponentForm[]
}

export interface PanelModuleForm {
  brand: string
  model: string
  panel_type: PanelType
  cell_count?: number
  power_w: number
  panel_count: number
  warranty_start_date?: string
  product_warranty_years?: number
  hardware_warranty_years?: number
  performance_warranty_years?: number
}

export interface BosComponentForm {
  component_type: BosComponentType
  brand: string
  model: string
  quantity: number
}
