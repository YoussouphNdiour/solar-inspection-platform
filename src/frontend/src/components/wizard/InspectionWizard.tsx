import React, { useRef, useState } from 'react'
import { inspectionsApi } from '../../api/inspections'
import { sitesApi } from '../../api/sites'
import type { InspectionFormData, InspectionResponse, PlanType } from '../../types/inspection'
import type { Site } from '../../types/site'
import { InspStep1PlanSelect } from './InspStep1PlanSelect'
import { InspStep2DroneInfo } from './InspStep2DroneInfo'
import { InspStep3Review } from './InspStep3Review'
import { InspStep4Payment } from './InspStep4Payment'

// ─── Steps config ─────────────────────────────────────────────────────────────

const STEPS = [
  { index: 1, label: 'Plan', icon: '📋' },
  { index: 2, label: 'Drone', icon: '🚁' },
  { index: 3, label: 'Révision', icon: '🔍' },
  { index: 4, label: 'Paiement', icon: '💳' },
]

// ─── Progress bar ─────────────────────────────────────────────────────────────

interface ProgressBarProps {
  currentStep: number
}

const ProgressBar: React.FC<ProgressBarProps> = ({ currentStep }) => (
  <div className="bg-[#2a2a2a] rounded-xl p-4 mb-6">
    <div className="flex items-center justify-between relative">
      {/* Connecting line — background */}
      <div className="absolute top-4 left-0 right-0 h-0.5 bg-gray-700 z-0" />
      {/* Connecting line — progress */}
      <div
        className="absolute top-4 left-0 h-0.5 bg-amber-500 z-0 transition-all duration-300"
        style={{ width: `${((currentStep - 1) / (STEPS.length - 1)) * 100}%` }}
      />

      {STEPS.map((step) => {
        const isCompleted = currentStep > step.index
        const isCurrent = currentStep === step.index
        return (
          <div key={step.index} className="flex flex-col items-center z-10 relative">
            <div
              className={`
                w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold border-2 transition-all
                ${isCompleted
                  ? 'bg-amber-500 border-amber-500 text-black'
                  : isCurrent
                  ? 'bg-[#2a2a2a] border-amber-500 text-amber-500'
                  : 'bg-[#2a2a2a] border-gray-600 text-gray-500'
                }
              `}
            >
              {isCompleted ? '✓' : step.index}
            </div>
            <span
              className={`mt-2 text-xs ${
                isCurrent
                  ? 'text-amber-500 font-semibold'
                  : isCompleted
                  ? 'text-gray-300'
                  : 'text-gray-500'
              }`}
            >
              {step.label}
            </span>
          </div>
        )
      })}
    </div>
  </div>
)

// ─── Main wizard ──────────────────────────────────────────────────────────────

export const InspectionWizard: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(1)
  const [formData, setFormData] = useState<Partial<InspectionFormData>>({
    plan_type: undefined,
    site_id: '',
    drone_manufacturer: '',
    drone_model: '',
    drone_serial_number: '',
    flight_date: '',
  })
  const [selectedSite, setSelectedSite] = useState<Site | null>(null)
  const [inspection, setInspection] = useState<InspectionResponse | null>(null)
  const [isCreating, setIsCreating] = useState(false)
  const [createError, setCreateError] = useState<string | null>(null)

  // Ref to imperatively submit Step2 form
  const step2FormRef = useRef<HTMLFormElement>(null)

  // ─── Step 1 handlers ────────────────────────────────────────────────────────

  const handlePlanChange = (plan: PlanType) => {
    setFormData((prev) => ({ ...prev, plan_type: plan }))
  }

  const handleSiteChange = async (siteId: string) => {
    setFormData((prev) => ({ ...prev, site_id: siteId }))
    try {
      const site = await sitesApi.get(siteId)
      setSelectedSite(site)
    } catch {
      setSelectedSite(null)
    }
  }

  const canProceedStep1 = !!formData.plan_type && !!formData.site_id

  // ─── Step 2 handlers ────────────────────────────────────────────────────────

  const handleStep2Submit = (data: Pick<InspectionFormData, 'drone_manufacturer' | 'drone_model' | 'drone_serial_number' | 'flight_date'>) => {
    setFormData((prev) => ({ ...prev, ...data }))
    setCurrentStep(3)
  }

  // ─── Step 3 handler — create inspection then go to step 4 ──────────────────

  const handleProceedToPayment = async () => {
    if (!formData.plan_type || !formData.site_id) return

    setIsCreating(true)
    setCreateError(null)
    try {
      const payload = {
        plan_type: formData.plan_type,
        site_id: formData.site_id,
        drone_manufacturer: formData.drone_manufacturer,
        drone_model: formData.drone_model,
        drone_serial_number: formData.drone_serial_number,
        flight_date: formData.flight_date || undefined,
      }
      const created = await inspectionsApi.create(payload)
      setInspection(created)
      setCurrentStep(4)
    } catch {
      setCreateError("Erreur lors de la création de l'inspection. Veuillez réessayer.")
    } finally {
      setIsCreating(false)
    }
  }

  // ─── Navigation ─────────────────────────────────────────────────────────────

  const handleNext = () => {
    if (currentStep === 1 && canProceedStep1) {
      setCurrentStep(2)
    } else if (currentStep === 2) {
      // Trigger the Step2 form submission imperatively
      step2FormRef.current?.requestSubmit()
    }
  }

  const handleBack = () => {
    setCurrentStep((s) => Math.max(s - 1, 1))
  }

  const isLastNavigableStep = currentStep >= 3

  return (
    <div className="space-y-0">
      {/* Progress bar */}
      <ProgressBar currentStep={currentStep} />

      {/* Step content */}
      <div className="bg-[#1a1a1a] rounded-xl border border-gray-800">
        {currentStep === 1 && (
          <InspStep1PlanSelect
            selectedPlan={formData.plan_type ?? null}
            selectedSiteId={formData.site_id ?? ''}
            onPlanChange={handlePlanChange}
            onSiteChange={handleSiteChange}
          />
        )}

        {currentStep === 2 && (
          <InspStep2DroneInfo
            formData={formData}
            onSubmit={handleStep2Submit}
            formRef={step2FormRef}
          />
        )}

        {currentStep === 3 && (
          <>
            {createError && (
              <div className="mx-6 mt-4 rounded-lg bg-red-500/10 border border-red-500/30 px-3 py-2 text-xs text-red-400">
                {createError}
              </div>
            )}
            <InspStep3Review
              formData={formData as InspectionFormData}
              site={selectedSite}
              onProceedToPayment={handleProceedToPayment}
              isCreating={isCreating}
            />
          </>
        )}

        {currentStep === 4 && inspection && (
          <InspStep4Payment inspection={inspection} site={selectedSite} />
        )}
      </div>

      {/* Navigation buttons — shown on steps 1 & 2 only */}
      {!isLastNavigableStep && (
        <div className="flex justify-between gap-4 mt-4">
          <button
            type="button"
            onClick={handleBack}
            disabled={currentStep === 1}
            className="px-6 py-2.5 rounded-lg border border-gray-600 text-gray-300 hover:bg-gray-800 disabled:opacity-30 disabled:cursor-not-allowed text-sm font-medium transition-colors"
          >
            ← Précédent
          </button>
          <button
            type="button"
            onClick={handleNext}
            disabled={currentStep === 1 && !canProceedStep1}
            className="px-6 py-2.5 rounded-lg bg-amber-500 hover:bg-amber-600 disabled:opacity-40 disabled:cursor-not-allowed text-black font-semibold text-sm transition-colors"
          >
            Suivant →
          </button>
        </div>
      )}

      {/* Back button on step 3 */}
      {currentStep === 3 && (
        <div className="flex justify-start mt-4">
          <button
            type="button"
            onClick={handleBack}
            className="px-6 py-2.5 rounded-lg border border-gray-600 text-gray-300 hover:bg-gray-800 text-sm font-medium transition-colors"
          >
            ← Précédent
          </button>
        </div>
      )}

      {/* Back button on step 4 */}
      {currentStep === 4 && (
        <div className="flex justify-start mt-4">
          <button
            type="button"
            onClick={handleBack}
            className="px-6 py-2.5 rounded-lg border border-gray-600 text-gray-300 hover:bg-gray-800 text-sm font-medium transition-colors"
          >
            ← Précédent
          </button>
        </div>
      )}
    </div>
  )
}
