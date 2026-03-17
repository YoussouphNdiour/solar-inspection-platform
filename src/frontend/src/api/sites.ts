import { apiClient } from './client'
import type { Site, SiteCreate } from '../types'

export const sitesApi = {
  list: async (skip = 0, limit = 20): Promise<Site[]> => {
    const { data } = await apiClient.get<Site[]>('/sites/', { params: { skip, limit } })
    return data
  },

  get: async (siteId: string): Promise<Site> => {
    const { data } = await apiClient.get<Site>(`/sites/${siteId}`)
    return data
  },

  create: async (payload: SiteCreate): Promise<Site> => {
    const { data } = await apiClient.post<Site>('/sites/', payload)
    return data
  },

  update: async (siteId: string, payload: Partial<SiteCreate>): Promise<Site> => {
    const { data } = await apiClient.put<Site>(`/sites/${siteId}`, payload)
    return data
  },

  delete: async (siteId: string): Promise<void> => {
    await apiClient.delete(`/sites/${siteId}`)
  },
}
