import { create } from 'zustand'
import type { Inspection, InspectionStatus } from '../types'
import { inspectionsApi } from '../api/inspections'

interface InspectionStore {
  inspections: Inspection[]
  selectedInspectionId: string | null
  isLoading: boolean
  error: string | null
  fetchInspections: (siteId?: string, status?: InspectionStatus) => Promise<void>
  selectInspection: (id: string | null) => void
}

export const useInspectionStore = create<InspectionStore>((set) => ({
  inspections: [],
  selectedInspectionId: null,
  isLoading: false,
  error: null,

  fetchInspections: async (siteId, status) => {
    set({ isLoading: true, error: null })
    try {
      const inspections = await inspectionsApi.list(siteId, status)
      set({ inspections, isLoading: false })
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erreur lors du chargement'
      set({ error: message, isLoading: false })
    }
  },

  selectInspection: (id) => set({ selectedInspectionId: id }),
}))
