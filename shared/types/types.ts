/**
 * Types TypeScript partagés — mirror des modèles Pydantic shared/types/models.py
 * Synchronisé manuellement (en production : généré via openapi-typescript)
 */

export type CoAClass = 'CoA1' | 'CoA2' | 'CoA3';

export type AnomalyType =
  | 'hotspot_cellule'
  | 'bypass_diode'
  | 'pid'
  | 'string_ouverte'
  | 'ombrage'
  | 'salissure'
  | 'sain';

export type DroneModel = 'DJI Mavic 3T' | 'Matrice 30T' | 'Matrice 300 RTK';

export type InspectionStatus = 'planned' | 'in_progress' | 'completed' | 'failed';

export interface GeoJSONPoint {
  type: 'Point';
  coordinates: [number, number]; // [longitude, latitude]
}

export interface GeoJSONPolygon {
  type: 'Polygon';
  coordinates: number[][][];
}

export interface Site {
  id: string;
  name: string;
  location: GeoJSONPoint;
  surface_m2: number;
  panel_count: number;
  created_at: string; // ISO 8601
}

export interface Inspection {
  id: string;
  site_id: string;
  drone_id: string | null;
  status: InspectionStatus;
  started_at: string | null;
  completed_at: string | null;
  irradiance_wm2: number | null;
  wind_speed_ms: number | null;
  ambient_temp_c: number | null;
  created_at: string;
}

export interface AnomalyProperties {
  panel_id: string;
  delta_t_measured: number;
  delta_t_normalized: number;
  coa_class: CoAClass;
  anomaly_type: AnomalyType;
  confidence: number;
  thermal_image_crop?: string;
  rgb_image_crop?: string;
}

export interface AnomalyFeature {
  type: 'Feature';
  geometry: GeoJSONPolygon;
  properties: AnomalyProperties;
}

export interface AnomalyGeoJSON {
  type: 'FeatureCollection';
  inspection_id: string;
  summary: {
    total_panels: number;
    anomaly_count: number;
    coa1: number;
    coa2: number;
    coa3: number;
    estimated_power_loss_pct: number;
  };
  features: AnomalyFeature[];
}

export interface FlightPlan {
  site_id: string;
  drone_model: DroneModel;
  generated_at: string;
  flight_plan: {
    altitude_m: number;
    speed_ms: number;
    frontal_overlap_pct: number;
    lateral_overlap_pct: number;
    gsd_rgb_cm: number;
    gsd_thermal_cm: number;
    estimated_duration_min: number;
    battery_cycles: number;
    total_waypoints: number;
  };
  waypoints: Array<{ lat: number; lon: number; alt: number }>;
}
