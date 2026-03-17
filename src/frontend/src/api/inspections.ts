import { apiClient } from './client'
import type { Inspection, InspectionCreate, InspectionStatus } from '../types'
import type { AnomalyGeoJSON } from '../types'

export const inspectionsApi = {
  list: async (siteId?: string, status?: InspectionStatus): Promise<Inspection[]> => {
    const { data } = await apiClient.get<Inspection[]>('/inspections/', {
      params: { site_id: siteId, status },
    })
    return data
  },

  get: async (inspectionId: string): Promise<Inspection> => {
    const { data } = await apiClient.get<Inspection>(`/inspections/${inspectionId}`)
    return data
  },

  create: async (payload: InspectionCreate): Promise<Inspection> => {
    const { data } = await apiClient.post<Inspection>('/inspections/', payload)
    return data
  },

  updateStatus: async (inspectionId: string, status: InspectionStatus): Promise<Inspection> => {
    const { data } = await apiClient.patch<Inspection>(
      `/inspections/${inspectionId}/status`,
      { status }
    )
    return data
  },

  getAnomalies: async (inspectionId: string): Promise<AnomalyGeoJSON> => {
    const { data } = await apiClient.get<AnomalyGeoJSON>(
      `/inspections/${inspectionId}/anomalies`
    )
    return data
  },
}
