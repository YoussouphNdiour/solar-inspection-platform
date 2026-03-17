import { create } from 'zustand'
import type { InspectionResponse, InspectionStatus } from '../types/inspection'
import { inspectionsApi } from '../api/inspections'

interface InspectionStore {
  inspections: InspectionResponse[]
  selectedInspectionId: string | null
  currentInspection: InspectionResponse | null
  isLoading: boolean
  error: string | null
  fetchInspections: (siteId?: string, status?: InspectionStatus) => Promise<void>
  createInspection: (data: object) => Promise<InspectionResponse>
  selectInspection: (id: string | null) => void
  setCurrentInspection: (inspection: InspectionResponse) => void
}

export const useInspectionStore = create<InspectionStore>((set) => ({
  inspections: [],
  selectedInspectionId: null,
  currentInspection: null,
  isLoading: false,
  error: null,

  fetchInspections: async (siteId, _status) => {
    set({ isLoading: true, error: null })
    try {
      const inspections = await inspectionsApi.list(siteId)
      set({ inspections, isLoading: false })
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erreur lors du chargement'
      set({ error: message, isLoading: false })
    }
  },

  createInspection: async (data) => {
    const inspection = await inspectionsApi.create(data)
    set((state) => ({ inspections: [...state.inspections, inspection] }))
    return inspection
  },

  selectInspection: (id) => set({ selectedInspectionId: id }),

  setCurrentInspection: (inspection) => set({ currentInspection: inspection }),
}))
