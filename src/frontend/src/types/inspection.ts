export type InspectionStatus = 'planned' | 'in_progress' | 'completed' | 'failed'

export interface Inspection {
  id: string
  site_id: string
  drone_id: string | null
  status: InspectionStatus
  started_at: string | null
  completed_at: string | null
  irradiance_wm2: number | null
  wind_speed_ms: number | null
  ambient_temp_c: number | null
  created_at: string
}

export interface InspectionCreate {
  site_id: string
  drone_id?: string
  irradiance_wm2?: number
  wind_speed_ms?: number
  ambient_temp_c?: number
}
