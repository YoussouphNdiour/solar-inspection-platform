import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { inspectionsApi } from '../../api/inspections'
import type { InspectionResponse, PlanType } from '../../types/inspection'
import type { Site } from '../../types/site'

// ─── Helpers ──────────────────────────────────────────────────────────────────

function getPlanLabel(planType: PlanType): string {
  return planType === 'professional_5gsd' ? 'Professional 5 GSD' : 'Enterprise 3 GSD'
}

// ─── Props ────────────────────────────────────────────────────────────────────

interface InspStep4PaymentProps {
  inspection: InspectionResponse
  site: Site | null
}

// ─── Component ────────────────────────────────────────────────────────────────

export const InspStep4Payment: React.FC<InspStep4PaymentProps> = ({ inspection, site }) => {
  const navigate = useNavigate()
  const [simulating, setSimulating] = useState(false)
  const [paid, setPaid] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSimulatePayment = async () => {
    setSimulating(true)
    setError(null)
    try {
      await inspectionsApi.updatePayment(inspection.id, 'paid')
      setPaid(true)
      setTimeout(() => {
        navigate(`/inspections/${inspection.id}/upload`)
      }, 1500)
    } catch {
      setError('Erreur lors de la simulation du paiement. Veuillez réessayer.')
    } finally {
      setSimulating(false)
    }
  }

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-lg font-semibold text-white">Paiement</h2>

      {/* Summary */}
      <div className="bg-[#2a2a2a] rounded-xl p-5 space-y-3">
        <h3 className="text-amber-400 font-semibold text-sm uppercase tracking-wider">
          Récapitulatif de la commande
        </h3>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-400">Centrale</span>
            <span className="text-white font-medium">{site?.name ?? inspection.site_id}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Plan</span>
            <span className="text-white font-medium">{getPlanLabel(inspection.plan_type)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Frais de service</span>
            <span className="text-white font-medium">${inspection.service_fee_usd.toFixed(2)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Commission bancaire ({inspection.bank_commission_pct}%)</span>
            <span className="text-white font-medium">
              ${(inspection.service_fee_usd * (inspection.bank_commission_pct / 100)).toFixed(2)}
            </span>
          </div>
          <div className="flex justify-between border-t border-gray-600 pt-2 font-bold text-base">
            <span className="text-white">Total</span>
            <span className="text-amber-400 text-lg">${inspection.total_amount_usd.toFixed(2)}</span>
          </div>
        </div>
      </div>

      {/* Payment options */}
      <div className="space-y-3">
        <button
          type="button"
          disabled
          className="w-full py-3 rounded-xl bg-amber-500/30 border border-amber-500/50 text-amber-300 font-semibold text-sm cursor-not-allowed flex items-center justify-center gap-2"
        >
          💳 Payer par carte (Stripe)
          <span className="text-xs font-normal text-amber-400/60">(bientôt disponible)</span>
        </button>

        <button
          type="button"
          disabled
          className="w-full py-3 rounded-xl bg-green-500/20 border border-green-500/40 text-green-400 font-semibold text-sm cursor-not-allowed flex items-center justify-center gap-2"
        >
          📱 Wave / Orange Money
          <span className="text-xs font-normal text-green-400/60">(bientôt disponible)</span>
        </button>
      </div>

      {/* Demo section */}
      <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-4 space-y-3">
        <p className="text-gray-400 text-xs text-center">
          Pour la démo, cliquez "Simuler le paiement"
        </p>

        {error && (
          <div className="rounded-lg bg-red-500/10 border border-red-500/30 px-3 py-2 text-xs text-red-400">
            {error}
          </div>
        )}

        {paid && (
          <div className="rounded-lg bg-green-500/10 border border-green-500/30 px-3 py-2 text-xs text-green-400 text-center">
            ✅ Paiement confirmé ! Redirection vers le téléchargement...
          </div>
        )}

        {!paid && (
          <button
            type="button"
            onClick={handleSimulatePayment}
            disabled={simulating}
            className="w-full py-3 rounded-xl bg-gray-700 hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-sm transition-colors flex items-center justify-center gap-2"
          >
            {simulating ? (
              <>
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Simulation en cours...
              </>
            ) : (
              '✅ Simuler le paiement'
            )}
          </button>
        )}
      </div>
    </div>
  )
}
