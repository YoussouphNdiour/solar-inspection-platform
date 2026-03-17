import React, { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

import { SiteFormData, SiteType, PanelModuleForm, BosComponentForm } from '../../types/site'
import { Step1BasicInfo } from './Step1BasicInfo'
import { Step2Panels } from './Step2Panels'
import { Step3BOS } from './Step3BOS'
import { Step4Confirm } from './Step4Confirm'

// ─── Zod schema ─────────────────────────────────────────────────────────────

const step1Schema = z.object({
  site_type: z.enum(['ground', 'rooftop', 'residential', 'floating']),
  name: z.string().min(1, 'Le nom est requis'),
  installation_date: z.string().min(1, 'La date est requise'),
  mounting_type: z.enum(['fixed', 'tracker_single_axis', 'tracker_dual_axis']),
  tilt_angle_deg: z
    .number({ invalid_type_error: "L'angle doit être un nombre" })
    .min(0)
    .max(90),
  azimuth_direction: z.enum(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']),
  azimuth_degrees: z
    .number({ invalid_type_error: "L'azimut doit être un nombre" })
    .min(0)
    .max(360),
  dc_power_installed_kw: z
    .number({ invalid_type_error: 'La puissance doit être un nombre' })
    .positive('La puissance doit être positive'),
  dc_power_unit: z.enum(['kW', 'MW']),
  energy_sale_price: z
    .number({ invalid_type_error: 'Le prix doit être un nombre' })
    .nonnegative(),
  currency: z.string().min(1),
  address_line1: z.string().min(1, "L'adresse est requise"),
  address_line2: z.string().optional(),
  district: z.string().min(1, 'Le district est requis'),
  city: z.string().min(1, 'La ville est requise'),
  state_province: z.string().optional(),
  country: z.string().min(1, 'Le pays est requis'),
  postal_code: z.string().optional(),
  latitude: z
    .number({ invalid_type_error: 'La latitude doit être un nombre' })
    .min(-90, 'Latitude invalide')
    .max(90, 'Latitude invalide'),
  longitude: z
    .number({ invalid_type_error: 'La longitude doit être un nombre' })
    .min(-180, 'Longitude invalide')
    .max(180, 'Longitude invalide'),
  kml_file: z.any().optional(),
  panels: z.array(z.any()).default([]),
  bos_components: z.array(z.any()).default([]),
})

// ─── Steps config ────────────────────────────────────────────────────────────

const STEPS = [
  { label: 'Informations', index: 1 },
  { label: 'Panneaux', index: 2 },
  { label: 'Composants BOS', index: 3 },
  { label: 'Confirmation', index: 4 },
]

// ─── Toast ───────────────────────────────────────────────────────────────────

interface ToastState {
  message: string
  type: 'success' | 'error'
}

// ─── Main wizard ─────────────────────────────────────────────────────────────

export const SiteWizard: React.FC = () => {
  const navigate = useNavigate()
  const [currentStep, setCurrentStep] = useState(1)
  const [panels, setPanels] = useState<PanelModuleForm[]>([])
  const [bosComponents, setBosComponents] = useState<BosComponentForm[]>([])
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [toast, setToast] = useState<ToastState | null>(null)

  const {
    register,
    control,
    watch,
    setValue,
    getValues,
    trigger,
    formState: { errors },
  } = useForm<SiteFormData>({
    resolver: zodResolver(step1Schema),
    defaultValues: {
      site_type: 'ground',
      mounting_type: 'fixed',
      tilt_angle_deg: 30,
      azimuth_direction: 'S',
      azimuth_degrees: 180,
      dc_power_unit: 'kW',
      currency: 'USD',
      panels: [],
      bos_components: [],
    },
  })

  const watchSiteType = watch('site_type')

  const showToast = (message: string, type: 'success' | 'error') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 4000)
  }

  const handleNext = async () => {
    if (currentStep === 1) {
      const valid = await trigger([
        'site_type', 'name', 'installation_date', 'mounting_type',
        'tilt_angle_deg', 'azimuth_direction', 'azimuth_degrees',
        'dc_power_installed_kw', 'dc_power_unit', 'energy_sale_price',
        'currency', 'address_line1', 'district', 'city', 'country',
        'latitude', 'longitude',
      ])
      if (!valid) return
    }
    setCurrentStep((s) => Math.min(s + 1, 4))
  }

  const handleBack = () => {
    setCurrentStep((s) => Math.max(s - 1, 1))
  }

  const handleCreate = async () => {
    const formValues = getValues()
    const fullData: SiteFormData = {
      ...formValues,
      panels,
      bos_components: bosComponents,
    }

    setIsSubmitting(true)
    try {
      // Create site
      const sitePayload = {
        name: fullData.name,
        site_type: fullData.site_type,
        installation_date: fullData.installation_date,
        mounting_type: fullData.mounting_type,
        tilt_angle_deg: fullData.tilt_angle_deg,
        azimuth_direction: fullData.azimuth_direction,
        azimuth_degrees: fullData.azimuth_degrees,
        dc_power_installed_kw: fullData.dc_power_installed_kw,
        dc_power_unit: fullData.dc_power_unit,
        energy_sale_price: fullData.energy_sale_price,
        currency: fullData.currency,
        address_line1: fullData.address_line1,
        address_line2: fullData.address_line2,
        district: fullData.district,
        city: fullData.city,
        state_province: fullData.state_province,
        country: fullData.country,
        postal_code: fullData.postal_code,
        latitude: fullData.latitude,
        longitude: fullData.longitude,
      }

      const siteRes = await axios.post('/api/v1/sites', sitePayload)
      const siteId: string = siteRes.data.id

      // Create panels
      for (const panel of fullData.panels) {
        await axios.post(`/api/v1/sites/${siteId}/panels`, panel)
      }

      // Create BOS components
      for (const bos of fullData.bos_components) {
        await axios.post(`/api/v1/sites/${siteId}/bos`, bos)
      }

      showToast('Centrale créée avec succès !', 'success')
      setTimeout(() => navigate(`/sites/${siteId}`), 1000)
    } catch (err: unknown) {
      const message =
        axios.isAxiosError(err) && err.response?.data?.detail
          ? err.response.data.detail
          : 'Une erreur est survenue lors de la création.'
      showToast(message, 'error')
    } finally {
      setIsSubmitting(false)
    }
  }

  const currentFormData: SiteFormData = {
    ...getValues(),
    panels,
    bos_components: bosComponents,
  }

  return (
    <div className="space-y-6">
      {/* Toast */}
      {toast && (
        <div
          className={`fixed top-4 right-4 z-50 px-5 py-3 rounded-lg shadow-lg text-sm font-medium transition-all ${
            toast.type === 'success'
              ? 'bg-green-600 text-white'
              : 'bg-red-600 text-white'
          }`}
        >
          {toast.message}
        </div>
      )}

      {/* Progress bar */}
      <div className="bg-[#2a2a2a] rounded-xl p-4">
        <div className="flex items-center justify-between relative">
          {/* Connecting line */}
          <div className="absolute top-4 left-0 right-0 h-0.5 bg-gray-700 z-0" />
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
                    ${
                      isCompleted
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
                    isCurrent ? 'text-amber-500 font-semibold' : isCompleted ? 'text-gray-300' : 'text-gray-500'
                  }`}
                >
                  {step.label}
                </span>
              </div>
            )
          })}
        </div>
      </div>

      {/* Step content */}
      <div className="bg-[#1a1a1a] rounded-xl">
        <form onSubmit={(e) => e.preventDefault()}>
          {currentStep === 1 && (
            <Step1BasicInfo
              register={register}
              errors={errors}
              control={control}
              watchSiteType={watchSiteType}
              onSiteTypeChange={(type: SiteType) => setValue('site_type', type)}
            />
          )}

          {currentStep === 2 && (
            <Step2Panels panels={panels} onPanelsChange={setPanels} />
          )}

          {currentStep === 3 && (
            <Step3BOS components={bosComponents} onComponentsChange={setBosComponents} />
          )}

          {currentStep === 4 && (
            <Step4Confirm
              formData={currentFormData}
              onSubmit={handleCreate}
              isSubmitting={isSubmitting}
            />
          )}
        </form>
      </div>

      {/* Navigation buttons */}
      {currentStep < 4 && (
        <div className="flex justify-between gap-4">
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
            className="px-6 py-2.5 rounded-lg bg-amber-500 hover:bg-amber-600 text-black font-semibold text-sm transition-colors"
          >
            Suivant →
          </button>
        </div>
      )}

      {currentStep === 4 && currentStep > 1 && (
        <div className="flex justify-start">
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
