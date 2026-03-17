import React from 'react'
import type { InspectionFormData, PlanType } from '../../types/inspection'
import type { Site } from '../../types/site'

// ─── Pricing helpers ─────────────────────────────────────────────────────────

const PRICE_PER_PANEL: Record<PlanType, number> = {
  professional_5gsd: 0.15,
  enterprise_3gsd: 0.25,
}

function getPlanLabel(planType: PlanType): string {
  return planType === 'professional_5gsd' ? 'Professional 5 GSD' : 'Enterprise 3 GSD'
}

function getGSDLabel(planType: PlanType): string {
  return planType === 'professional_5gsd' ? '5.0 cm' : '3.0 cm'
}

// ─── Props ────────────────────────────────────────────────────────────────────

interface InspStep3ReviewProps {
  formData: InspectionFormData
  site: Site | null
  onProceedToPayment: () => void
  isCreating: boolean
}

// ─── Component ────────────────────────────────────────────────────────────────

export const InspStep3Review: React.FC<InspStep3ReviewProps> = ({
  formData,
  site,
  onProceedToPayment,
  isCreating,
}) => {
  const panelCount = site?.panel_count ?? 0
  const pricePerPanel = PRICE_PER_PANEL[formData.plan_type]
  const serviceFee = parseFloat((panelCount * pricePerPanel).toFixed(2))
  const commission = parseFloat((serviceFee * 0.05).toFixed(2))
  const total = parseFloat((serviceFee + commission).toFixed(2))

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-lg font-semibold text-white">Récapitulatif de l'inspection</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Left column — Standard info */}
        <div className="bg-[#2a2a2a] rounded-xl p-5 space-y-3">
          <h3 className="text-amber-400 font-semibold text-sm uppercase tracking-wider flex items-center gap-2">
            📋 Informations sur le standard
          </h3>
          <div className="space-y-2 text-sm">
            <InfoRow label="Centrale" value={site?.name ?? '—'} />
            <InfoRow label="Nombre de panneaux" value={panelCount > 0 ? panelCount.toString() : '—'} />
            <InfoRow label="Plan" value={getPlanLabel(formData.plan_type)} />
            <InfoRow label="GSD cible" value={getGSDLabel(formData.plan_type)} />
            {formData.flight_date && (
              <InfoRow label="Date de vol" value={formData.flight_date} />
            )}
          </div>
        </div>

        {/* Right column — Drone & pricing */}
        <div className="bg-[#2a2a2a] rounded-xl p-5 space-y-3">
          <h3 className="text-amber-400 font-semibold text-sm uppercase tracking-wider flex items-center gap-2">
            🚁 Drone & Paiement
          </h3>
          <div className="space-y-2 text-sm">
            <InfoRow label="Fabricant" value={formData.drone_manufacturer || '—'} />
            <InfoRow label="Modèle" value={formData.drone_model || '—'} />
            <InfoRow label="N° série" value={formData.drone_serial_number || '—'} />
          </div>

          <div className="border-t border-gray-600 pt-3 space-y-2 text-sm">
            <div className="flex justify-between text-gray-300">
              <span>Frais de service</span>
              <span>${serviceFee.toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-gray-400">
              <span>Commission bancaire (5%)</span>
              <span>${commission.toFixed(2)}</span>
            </div>
            <div className="flex justify-between font-bold text-base pt-1 border-t border-gray-700">
              <span className="text-white">Total</span>
              <span className="text-amber-400 text-lg">${total.toFixed(2)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Proceed button */}
      <button
        type="button"
        onClick={onProceedToPayment}
        disabled={isCreating}
        className="w-full py-3 rounded-xl bg-amber-500 hover:bg-amber-600 disabled:opacity-50 disabled:cursor-not-allowed text-black font-bold text-sm transition-colors flex items-center justify-center gap-2"
      >
        {isCreating ? (
          <>
            <span className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin" />
            Création en cours...
          </>
        ) : (
          'Procéder au paiement →'
        )}
      </button>
    </div>
  )
}

// ─── Subcomponent ─────────────────────────────────────────────────────────────

const InfoRow: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <div className="flex justify-between">
    <span className="text-gray-400">{label}</span>
    <span className="text-white font-medium text-right max-w-[55%] truncate">{value}</span>
  </div>
)
