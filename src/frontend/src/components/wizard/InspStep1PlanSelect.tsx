import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { sitesApi } from '../../api/sites'
import type { Site } from '../../types/site'
import type { PlanType, InspectionPricing } from '../../types/inspection'

// ─── Pricing config ──────────────────────────────────────────────────────────

const PRICE_PER_PANEL: Record<PlanType, number> = {
  professional_5gsd: 0.15,
  enterprise_3gsd: 0.25,
}

function computePricing(panelCount: number, planType: PlanType): InspectionPricing {
  const price_per_panel = PRICE_PER_PANEL[planType]
  const service_fee = parseFloat((panelCount * price_per_panel).toFixed(2))
  const bank_commission = parseFloat((service_fee * 0.05).toFixed(2))
  const total = parseFloat((service_fee + bank_commission).toFixed(2))
  return { panel_count: panelCount, plan_type: planType, price_per_panel, service_fee, bank_commission, total }
}

// ─── Anomaly type lists ───────────────────────────────────────────────────────

const THERMAL_TYPES = [
  'Cellule', 'Multi Cellule', 'Point Chaud', 'Multi Point Chaud',
  'Diode Circuit Ouvert', 'Diode Court-Circuit', 'Multi Diode Circuit Ouvert',
  'Multi Diode Court-Circuit', 'Module Circuit Ouvert', 'Module Court-Circuit',
  'String Circuit Ouvert', 'String Court-Circuit', 'Boîte de Jonction', 'PID', 'Polarité',
]

const RGB_TYPES = ['Salissure', 'Ombrage', 'Corps Étranger', 'Fissure', 'Délaminage']

// ─── Plan card ────────────────────────────────────────────────────────────────

interface PlanCardProps {
  planType: PlanType
  selected: boolean
  onSelect: () => void
}

const PlanCard: React.FC<PlanCardProps> = ({ planType, selected, onSelect }) => {
  const isPro = planType === 'professional_5gsd'

  return (
    <button
      type="button"
      onClick={onSelect}
      className={`
        flex-1 rounded-xl p-5 text-left border-2 transition-all duration-200 cursor-pointer
        bg-[#2a2a2a]
        ${selected ? 'border-amber-500 shadow-lg shadow-amber-500/10' : 'border-gray-700 hover:border-gray-500'}
      `}
    >
      {/* Header */}
      <div className="mb-3">
        <h3 className="text-xl font-bold text-white">
          {isPro ? 'Professional' : 'Enterprise'}
        </h3>
        <p className="text-sm text-gray-400 mt-1">
          {isPro ? '5.0 ± 0.5 cm' : '3.0 ± 0.5 cm'}
          <span className="ml-2 text-xs text-gray-500 uppercase tracking-wider">GSD (PIXELS/CM)</span>
        </p>
      </div>

      {/* Badge */}
      {isPro ? (
        <div className="mb-4 rounded-lg bg-amber-500/10 border border-amber-500/30 px-3 py-2 text-xs text-amber-400">
          ⚠️ Altitude de vol plus élevée — certaines anomalies au niveau cellulaire peuvent être perdues dans l'image.
        </div>
      ) : (
        <div className="mb-4 rounded-lg bg-green-500/10 border border-green-500/30 px-3 py-2 text-xs text-green-400">
          ✅ Basé sur les normes IEC 62446-3, analyse de la plus haute précision au niveau cellulaire.
        </div>
      )}

      {/* Anomalies header */}
      <div className="mb-3">
        <span className="text-sm font-semibold text-amber-400">✓ Anomalies Détectées : 20 Types d'Anomalies</span>
      </div>

      {/* Thermal types */}
      <div className="mb-3">
        <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">Thermiques (15 types)</p>
        <div className="flex flex-wrap gap-1">
          {THERMAL_TYPES.map((t) => (
            <span key={t} className="px-2 py-0.5 rounded text-xs bg-gray-700 text-gray-300">
              {t}
            </span>
          ))}
        </div>
      </div>

      {/* RGB types */}
      <div>
        <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">RGB (5 types)</p>
        <div className="flex flex-wrap gap-1">
          {RGB_TYPES.map((t) => (
            <span key={t} className="px-2 py-0.5 rounded text-xs bg-gray-700 text-gray-300">
              {t}
            </span>
          ))}
        </div>
      </div>

      {/* Selected indicator */}
      {selected && (
        <div className="mt-4 flex items-center gap-2 text-amber-400 text-sm font-semibold">
          <span className="w-4 h-4 rounded-full bg-amber-500 flex items-center justify-center text-black text-xs">✓</span>
          Sélectionné
        </div>
      )}
    </button>
  )
}

// ─── Main component ───────────────────────────────────────────────────────────

interface InspStep1PlanSelectProps {
  selectedPlan: PlanType | null
  selectedSiteId: string
  onPlanChange: (plan: PlanType) => void
  onSiteChange: (siteId: string) => void
}

export const InspStep1PlanSelect: React.FC<InspStep1PlanSelectProps> = ({
  selectedPlan,
  selectedSiteId,
  onPlanChange,
  onSiteChange,
}) => {
  const [sites, setSites] = useState<Site[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    sitesApi
      .list(0, 100)
      .then((data) => setSites(data))
      .catch(() => setError('Impossible de charger les centrales.'))
      .finally(() => setLoading(false))
  }, [])

  const selectedSite = sites.find((s) => s.id === selectedSiteId)
  const pricing =
    selectedSite && selectedPlan
      ? computePricing(selectedSite.panel_count, selectedPlan)
      : null

  return (
    <div className="space-y-6 p-6">
      {/* Plan cards */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-4">Choisissez votre plan d'inspection</h2>
        <div className="flex gap-4">
          <PlanCard
            planType="professional_5gsd"
            selected={selectedPlan === 'professional_5gsd'}
            onSelect={() => onPlanChange('professional_5gsd')}
          />
          <PlanCard
            planType="enterprise_3gsd"
            selected={selectedPlan === 'enterprise_3gsd'}
            onSelect={() => onPlanChange('enterprise_3gsd')}
          />
        </div>
      </div>

      {/* Site selection */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-3">Sélectionnez la centrale</h2>

        {loading && (
          <div className="text-gray-400 text-sm py-4">Chargement des centrales...</div>
        )}

        {error && (
          <div className="text-red-400 text-sm py-4">{error}</div>
        )}

        {!loading && !error && sites.length === 0 && (
          <div className="bg-[#2a2a2a] rounded-xl p-5 text-center">
            <p className="text-gray-400 text-sm mb-3">Aucune centrale disponible.</p>
            <Link
              to="/sites/new"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-amber-500 hover:bg-amber-600 text-black text-sm font-semibold transition-colors"
            >
              ⚡ Créez d'abord une centrale
            </Link>
          </div>
        )}

        {!loading && !error && sites.length > 0 && (
          <div className="grid grid-cols-1 gap-2">
            {sites.map((site) => (
              <button
                key={site.id}
                type="button"
                onClick={() => onSiteChange(site.id)}
                className={`
                  flex items-center justify-between rounded-xl p-4 border-2 transition-all text-left
                  bg-[#2a2a2a]
                  ${selectedSiteId === site.id
                    ? 'border-amber-500 shadow-sm shadow-amber-500/10'
                    : 'border-gray-700 hover:border-gray-500'
                  }
                `}
              >
                <div>
                  <p className="text-white font-medium">{site.name}</p>
                  <p className="text-xs text-gray-400 mt-0.5">{site.panel_count} panneaux</p>
                </div>
                {selectedSiteId === site.id && (
                  <span className="w-5 h-5 rounded-full bg-amber-500 flex items-center justify-center text-black text-xs font-bold">✓</span>
                )}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Pricing summary */}
      {pricing && (
        <div className="bg-[#2a2a2a] rounded-xl p-5 border border-amber-500/20">
          <h3 className="text-amber-400 font-semibold text-sm uppercase tracking-wider mb-3">
            💰 Tarification
          </h3>
          <div className="space-y-1 text-sm text-gray-300">
            <div className="flex justify-between">
              <span>{pricing.panel_count} panneaux × ${pricing.price_per_panel.toFixed(2)}</span>
              <span className="text-white font-medium">${pricing.service_fee.toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-gray-400">
              <span>+ 5% commission bancaire</span>
              <span>${pricing.bank_commission.toFixed(2)}</span>
            </div>
            <div className="border-t border-gray-600 pt-2 mt-2 flex justify-between font-bold text-base">
              <span className="text-white">Total</span>
              <span className="text-amber-400">${pricing.total.toFixed(2)}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
