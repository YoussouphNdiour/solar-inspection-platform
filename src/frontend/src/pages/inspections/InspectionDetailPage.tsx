import React, { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { InspectionProgress } from '../../components/InspectionProgress'
import { inspectionsApi } from '../../api/inspections'
import type { InspectionResponse, ProgressStep } from '../../types/inspection'

export const InspectionDetailPage: React.FC = () => {
  const { inspectionId } = useParams<{ inspectionId: string }>()
  const navigate = useNavigate()
  const [inspection, setInspection] = useState<InspectionResponse | null>(null)
  const [steps, setSteps] = useState<ProgressStep[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!inspectionId) return
    const load = async () => {
      try {
        const [insp, progress] = await Promise.all([
          inspectionsApi.get(inspectionId),
          inspectionsApi.getProgress(inspectionId),
        ])
        setInspection(insp)
        setSteps((progress as { steps?: ProgressStep[] }).steps ?? [])
      } catch {
        // ignore
      } finally {
        setLoading(false)
      }
    }
    load()
    // Polling toutes les 10s
    const interval = setInterval(load, 10_000)
    return () => clearInterval(interval)
  }, [inspectionId])

  if (loading) return <div className="text-gray-400 p-6">Chargement...</div>
  if (!inspection) return <div className="text-red-400 p-6">Inspection non trouvée.</div>

  const statusColors: Record<string, string> = {
    created: 'bg-gray-600',
    images_uploaded: 'bg-blue-600',
    processing: 'bg-amber-500',
    analysis_done: 'bg-purple-600',
    report_ready: 'bg-green-600',
  }

  return (
    <div className="min-h-full bg-[#1a1a1a] p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold text-white">
              {inspection.site_name ?? 'Inspection'}
            </h1>
            <p className="text-gray-400 text-sm mt-1">
              {inspection.plan_type === 'professional_5gsd' ? 'Professional 5 GSD' : 'Enterprise 3 GSD'} •{' '}
              Créée le {new Date(inspection.created_at).toLocaleDateString('fr-FR')}
            </p>
          </div>
          <span
            className={`px-3 py-1 rounded-full text-xs font-semibold text-white ${
              statusColors[inspection.status] ?? 'bg-gray-600'
            }`}
          >
            {inspection.status.replace('_', ' ')}
          </span>
        </div>

        {/* Progression */}
        <div className="bg-[#2a2a2a] rounded-xl p-6">
          <h2 className="text-amber-500 font-semibold mb-4">Progression de l'examen</h2>
          <InspectionProgress
            steps={steps}
            currentStep={inspection.progression}
            onStepClick={(step) => {
              if (step === 1) navigate(`/inspections/${inspectionId}/upload`)
              if (step === 4) navigate(`/reports/${inspectionId}`)
            }}
          />
        </div>

        {/* Actions selon étape */}
        <div className="bg-[#2a2a2a] rounded-xl p-6 space-y-3">
          <h2 className="text-amber-500 font-semibold mb-2">Actions disponibles</h2>
          {inspection.payment_status === 'pending' && (
            <div className="flex items-center gap-3">
              <span className="text-red-400 text-sm">💳 Paiement en attente</span>
              <Link
                to="/inspections/new"
                className="text-xs bg-amber-500 text-black px-3 py-1.5 rounded font-semibold"
              >
                Compléter le paiement
              </Link>
            </div>
          )}
          {inspection.payment_status === 'paid' && inspection.progression < 2 && (
            <Link
              to={`/inspections/${inspectionId}/upload`}
              className="inline-flex items-center gap-2 bg-amber-500 text-black px-4 py-2 rounded font-semibold"
            >
              📤 Télécharger les images
            </Link>
          )}
          {inspection.progression >= 2 && inspection.progression < 3 && (
            <button
              onClick={async () => {
                await inspectionsApi.startAnalysis(inspectionId!)
                window.location.reload()
              }}
              className="bg-purple-600 text-white px-4 py-2 rounded font-semibold"
            >
              🔬 Lancer l'analyse IA
            </button>
          )}
          {inspection.progression >= 4 && (
            <Link
              to={`/reports/${inspectionId}`}
              className="inline-flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded font-semibold"
            >
              📄 Voir le rapport
            </Link>
          )}
        </div>

        {/* Tarification */}
        <div className="bg-[#2a2a2a] rounded-xl p-6">
          <h2 className="text-amber-500 font-semibold mb-3">Tarification</h2>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between text-gray-300">
              <span>Frais de service</span>
              <span>${inspection.service_fee_usd?.toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-gray-300">
              <span>Commission bancaire ({inspection.bank_commission_pct}%)</span>
              <span>
                ${((inspection.total_amount_usd ?? 0) - (inspection.service_fee_usd ?? 0)).toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between font-bold text-white text-base pt-2 border-t border-gray-600">
              <span>Total</span>
              <span className="text-amber-500">${inspection.total_amount_usd?.toFixed(2)}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
