export type PlanType = 'professional_5gsd' | 'enterprise_3gsd'
export type PaymentStatus = 'pending' | 'paid' | 'failed'
export type InspectionStatus = 'created' | 'images_uploaded' | 'processing' | 'analysis_done' | 'report_ready'

export interface InspectionFormData {
  plan_type: PlanType
  site_id: string
  drone_manufacturer: string
  drone_model: string
  drone_serial_number: string
  flight_date?: string
}

export interface InspectionPricing {
  panel_count: number
  plan_type: PlanType
  price_per_panel: number
  service_fee: number
  bank_commission: number
  total: number
}

export interface InspectionResponse {
  id: string
  site_id: string
  site_name?: string
  plan_type: PlanType
  gsd_target_cm: number
  drone_manufacturer?: string
  drone_model?: string
  drone_serial_number?: string
  service_fee_usd: number
  bank_commission_pct: number
  total_amount_usd: number
  payment_status: PaymentStatus
  status: InspectionStatus
  progression: number
  created_at: string
  report_data?: unknown
}

/** Alias de compatibilité */
export type Inspection = InspectionResponse
export type InspectionCreate = InspectionFormData

export interface ProgressStep {
  step: number
  label: string
  icon: string
  state: 'completed' | 'active' | 'locked'
}
