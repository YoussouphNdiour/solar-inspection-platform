import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useSiteStore } from '../../src/store/siteStore'

// Mock du module API
vi.mock('../../src/api/sites', () => ({
  sitesApi: {
    list: vi.fn(),
  },
}))

describe('useSiteStore', () => {
  beforeEach(() => {
    // Réinitialiser le store
    useSiteStore.setState({
      sites: [],
      selectedSiteId: null,
      isLoading: false,
      error: null,
    })
  })

  it('initialise avec un état vide', () => {
    const state = useSiteStore.getState()
    expect(state.sites).toEqual([])
    expect(state.selectedSiteId).toBeNull()
    expect(state.isLoading).toBe(false)
    expect(state.error).toBeNull()
  })

  it('selectSite met à jour selectedSiteId', () => {
    const { selectSite } = useSiteStore.getState()
    selectSite('site-123')
    expect(useSiteStore.getState().selectedSiteId).toBe('site-123')
  })

  it('selectSite accepte null pour désélectionner', () => {
    useSiteStore.setState({ selectedSiteId: 'site-123' })
    const { selectSite } = useSiteStore.getState()
    selectSite(null)
    expect(useSiteStore.getState().selectedSiteId).toBeNull()
  })

  it('addSite ajoute un site à la liste', () => {
    const mockSite = {
      id: 'site-001',
      name: 'Test',
      location: { type: 'Point' as const, coordinates: [-1.5, 43.5] as [number, number] },
      surface_m2: 1000,
      panel_count: 50,
      created_at: '2024-01-01T00:00:00Z',
    }
    const { addSite } = useSiteStore.getState()
    addSite(mockSite)
    expect(useSiteStore.getState().sites).toHaveLength(1)
    expect(useSiteStore.getState().sites[0].name).toBe('Test')
  })

  it('fetchSites gère les erreurs', async () => {
    const { sitesApi } = await import('../../src/api/sites')
    vi.mocked(sitesApi.list).mockRejectedValueOnce(new Error('Réseau indisponible'))

    const { fetchSites } = useSiteStore.getState()
    await fetchSites()

    const state = useSiteStore.getState()
    expect(state.isLoading).toBe(false)
    expect(state.error).toBe('Réseau indisponible')
    expect(state.sites).toEqual([])
  })

  it('fetchSites charge les sites avec succès', async () => {
    const mockSites = [
      {
        id: 'site-001',
        name: 'Centrale A',
        location: { type: 'Point' as const, coordinates: [-1.5, 43.5] as [number, number] },
        surface_m2: 5000,
        panel_count: 250,
        created_at: '2024-01-01T00:00:00Z',
      },
    ]
    const { sitesApi } = await import('../../src/api/sites')
    vi.mocked(sitesApi.list).mockResolvedValueOnce(mockSites)

    const { fetchSites } = useSiteStore.getState()
    await fetchSites()

    const state = useSiteStore.getState()
    expect(state.isLoading).toBe(false)
    expect(state.error).toBeNull()
    expect(state.sites).toEqual(mockSites)
  })
})
