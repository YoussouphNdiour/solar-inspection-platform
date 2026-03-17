import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { InspectionProgress } from '../../components/InspectionProgress'
import { inspectionsApi } from '../../api/inspections'
import type { InspectionResponse, ProgressStep } from '../../types/inspection'

export const ReportDetailPage: React.FC = () => {
  const { inspectionId } = useParams<{ inspectionId: string }>()
  const [inspection, setInspection] = useState<InspectionResponse | null>(null)
  const [steps, setSteps] = useState<ProgressStep[]>([])

  useEffect(() => {
    if (!inspectionId) return
    Promise.all([
      inspectionsApi.get(inspectionId),
      inspectionsApi.getProgress(inspectionId),
    ]).then(([insp, progress]) => {
      setInspection(insp)
      setSteps((progress as { steps?: ProgressStep[] }).steps ?? [])
    })
  }, [inspectionId])

  if (!inspection) return <div className="text-gray-400 p-6">Chargement...</div>

  const reportData = inspection.report_data as Record<string, unknown> | null

  return (
    <div className="min-h-full bg-[#1a1a1a] p-6">
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-white">
              {inspection.site_name ?? 'Centrale'}
            </h1>
            <p className="text-gray-400 text-sm">Rapport d'inspection drone • IEC 62446-3</p>
          </div>
          <button className="bg-amber-500 text-black px-4 py-2 rounded font-semibold">
            📥 Télécharger PDF
          </button>
        </div>

        {/* KPIs */}
        <div className="grid grid-cols-3 gap-4">
          {[
            { label: 'Puissance DC', value: '— kW', icon: '⚡' },
            { label: 'Panneaux sains', value: '—%', icon: '✅' },
            {
              label: 'Anomalies détectées',
              value: reportData
                ? String((reportData as { anomaly_count?: number }).anomaly_count ?? '—')
                : '—',
              icon: '⚠️',
            },
          ].map((kpi) => (
            <div key={kpi.label} className="bg-[#2a2a2a] rounded-xl p-5 text-center">
              <div className="text-3xl mb-2">{kpi.icon}</div>
              <div className="text-2xl font-bold text-white">{kpi.value}</div>
              <div className="text-xs text-gray-400 mt-1">{kpi.label}</div>
            </div>
          ))}
        </div>

        {/* Progression */}
        <div className="bg-[#2a2a2a] rounded-xl p-6">
          <h2 className="text-amber-500 font-semibold mb-4">Étapes de l'examen</h2>
          <InspectionProgress steps={steps} currentStep={inspection.progression} />
        </div>

        {/* Logo entreprise */}
        <div className="bg-[#2a2a2a] rounded-xl p-6">
          <h2 className="text-amber-500 font-semibold mb-3">Logo de l'entreprise (optionnel)</h2>
          <div className="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center text-gray-500">
            <p>Glissez votre logo ici pour le rapport PDF</p>
            <button className="mt-3 text-amber-500 text-sm underline">Parcourir</button>
          </div>
        </div>

        {/* Bouton créer rapport */}
        {inspection.progression >= 4 ? (
          <button className="w-full bg-amber-500 text-black py-4 rounded-xl font-bold text-lg">
            📄 Créer le rapport PDF
          </button>
        ) : (
          <div className="bg-[#2a2a2a] rounded-xl p-4 text-center text-gray-400">
            Le rapport sera disponible une fois l'analyse terminée.
          </div>
        )}
      </div>
    </div>
  )
}
