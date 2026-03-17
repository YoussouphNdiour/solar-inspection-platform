import { create } from 'zustand'
import type { Site } from '../types'
import { sitesApi } from '../api/sites'

interface SiteStore {
  sites: Site[]
  selectedSiteId: string | null
  isLoading: boolean
  error: string | null
  fetchSites: () => Promise<void>
  selectSite: (id: string | null) => void
  addSite: (site: Site) => void
}

export const useSiteStore = create<SiteStore>((set) => ({
  sites: [],
  selectedSiteId: null,
  isLoading: false,
  error: null,

  fetchSites: async () => {
    set({ isLoading: true, error: null })
    try {
      const sites = await sitesApi.list()
      set({ sites, isLoading: false })
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erreur lors du chargement des sites'
      set({ error: message, isLoading: false })
    }
  },

  selectSite: (id) => set({ selectedSiteId: id }),

  addSite: (site) => set((state) => ({ sites: [...state.sites, site] })),
}))
