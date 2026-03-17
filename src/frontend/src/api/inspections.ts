import { apiClient } from './client'
import type { InspectionResponse } from '../types/inspection'

export const inspectionsApi = {
  create: (data: object) =>
    apiClient.post<InspectionResponse>('/inspections', data).then((r) => r.data),

  list: (siteId?: string) =>
    apiClient
      .get<InspectionResponse[]>('/inspections', {
        params: siteId ? { site_id: siteId } : {},
      })
      .then((r) => r.data),

  get: (id: string) =>
    apiClient.get<InspectionResponse>(`/inspections/${id}`).then((r) => r.data),

  updatePayment: (id: string, status: string) =>
    apiClient
      .put(`/inspections/${id}/payment`, { payment_status: status })
      .then((r) => r.data),

  uploadImages: (
    id: string,
    files: File[],
    onProgress?: (pct: number) => void
  ) => {
    const form = new FormData()
    files.forEach((f) => form.append('files', f))
    return apiClient
      .post(`/inspections/${id}/images`, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (e) =>
          onProgress &&
          onProgress(Math.round((e.loaded * 100) / (e.total ?? 1))),
      })
      .then((r) => r.data)
  },

  getImages: (id: string) =>
    apiClient.get(`/inspections/${id}/images`).then((r) => r.data),

  startAnalysis: (id: string) =>
    apiClient.post(`/inspections/${id}/start-analysis`).then((r) => r.data),

  getProgress: (id: string) =>
    apiClient.get(`/inspections/${id}/progress`).then((r) => r.data),

  getAnomalies: (id: string) =>
    apiClient.get(`/inspections/${id}/anomalies`).then((r) => r.data),
}
