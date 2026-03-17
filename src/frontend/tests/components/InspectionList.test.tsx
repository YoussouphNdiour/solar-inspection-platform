import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { InspectionList } from '../../src/components/InspectionList'
import { useInspectionStore } from '../../src/store/inspectionStore'

vi.mock('../../src/store/inspectionStore', () => ({
  useInspectionStore: vi.fn(),
}))

const mockUseInspectionStore = vi.mocked(useInspectionStore)

describe('InspectionList', () => {
  const mockFetchInspections = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('affiche un spinner pendant le chargement', () => {
    mockUseInspectionStore.mockReturnValue({
      inspections: [],
      isLoading: true,
      error: null,
      fetchInspections: mockFetchInspections,
      selectedInspectionId: null,
      selectInspection: vi.fn(),
    })

    render(
      <MemoryRouter>
        <InspectionList />
      </MemoryRouter>
    )

    // Le spinner est présent (div avec animate-spin)
    expect(document.querySelector('.animate-spin')).toBeTruthy()
  })

  it('affiche une erreur', () => {
    mockUseInspectionStore.mockReturnValue({
      inspections: [],
      isLoading: false,
      error: 'Connexion impossible',
      fetchInspections: mockFetchInspections,
      selectedInspectionId: null,
      selectInspection: vi.fn(),
    })

    render(
      <MemoryRouter>
        <InspectionList />
      </MemoryRouter>
    )

    expect(screen.getByText('Connexion impossible')).toBeTruthy()
  })

  it('affiche "Aucune inspection" si la liste est vide', () => {
    mockUseInspectionStore.mockReturnValue({
      inspections: [],
      isLoading: false,
      error: null,
      fetchInspections: mockFetchInspections,
      selectedInspectionId: null,
      selectInspection: vi.fn(),
    })

    render(
      <MemoryRouter>
        <InspectionList />
      </MemoryRouter>
    )

    expect(screen.getByText('Aucune inspection trouvée')).toBeTruthy()
  })

  it('affiche le nombre d\'inspections', () => {
    const mockInspections = [
      {
        id: 'insp-001',
        site_id: 'site-001',
        drone_id: null,
        status: 'completed' as const,
        started_at: '2024-07-15T08:00:00Z',
        completed_at: '2024-07-15T10:00:00Z',
        irradiance_wm2: 850,
        wind_speed_ms: 2.1,
        ambient_temp_c: 28,
        created_at: '2024-07-15T07:00:00Z',
      },
    ]

    mockUseInspectionStore.mockReturnValue({
      inspections: mockInspections,
      isLoading: false,
      error: null,
      fetchInspections: mockFetchInspections,
      selectedInspectionId: null,
      selectInspection: vi.fn(),
    })

    render(
      <MemoryRouter>
        <InspectionList />
      </MemoryRouter>
    )

    expect(screen.getByText('Inspections (1)')).toBeTruthy()
  })
})
