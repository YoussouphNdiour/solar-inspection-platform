import { create } from 'zustand'
import type { CoAClass } from '../types'

interface ViewState {
  latitude: number
  longitude: number
  zoom: number
}

interface MapStore {
  viewport: ViewState
  selectedAnomalyId: string | null
  coaFilter: CoAClass[]
  setViewport: (viewport: ViewState) => void
  selectAnomaly: (id: string | null) => void
  setCoaFilter: (filter: CoAClass[]) => void
  flyTo: (lat: number, lon: number, zoom?: number) => void
}

export const useMapStore = create<MapStore>((set) => ({
  viewport: { latitude: 46.6, longitude: 2.3, zoom: 5 },
  selectedAnomalyId: null,
  coaFilter: ['CoA1', 'CoA2', 'CoA3'],

  setViewport: (viewport) => set({ viewport }),
  selectAnomaly: (id) => set({ selectedAnomalyId: id }),
  setCoaFilter: (filter) => set({ coaFilter: filter }),
  flyTo: (lat, lon, zoom = 14) =>
    set({ viewport: { latitude: lat, longitude: lon, zoom } }),
}))
