import React from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import type { InspectionFormData } from '../../types/inspection'

// ─── Drone data ───────────────────────────────────────────────────────────────

const DRONE_MODELS: Record<string, string[]> = {
  DJI: ['Mavic 3T', 'Matrice 30T', 'Matrice 300 RTK + H20T', 'Mavic 2 Enterprise Advanced', 'M3E'],
  Parrot: ['ANAFI Thermal', 'ANAFI USA'],
  'Autel Robotics': ['EVO II Dual 640T', 'EVO Max 4T'],
  Autre: [],
}

const MANUFACTURERS = Object.keys(DRONE_MODELS)

// ─── Zod schema ───────────────────────────────────────────────────────────────

const droneSchema = z.object({
  drone_manufacturer: z.string().min(1, 'Le fabricant est requis'),
  drone_model: z.string().min(1, 'Le modèle est requis'),
  drone_serial_number: z
    .string()
    .min(3, 'Le numéro de série doit avoir au moins 3 caractères'),
  flight_date: z.string().optional(),
})

type DroneFormValues = z.infer<typeof droneSchema>

// ─── Props ────────────────────────────────────────────────────────────────────

interface InspStep2DroneInfoProps {
  formData: Partial<InspectionFormData>
  onSubmit: (data: Pick<InspectionFormData, 'drone_manufacturer' | 'drone_model' | 'drone_serial_number' | 'flight_date'>) => void
  formRef: React.RefObject<HTMLFormElement>
}

// ─── Component ────────────────────────────────────────────────────────────────

export const InspStep2DroneInfo: React.FC<InspStep2DroneInfoProps> = ({
  formData,
  onSubmit,
  formRef,
}) => {
  const {
    register,
    watch,
    handleSubmit,
    formState: { errors },
  } = useForm<DroneFormValues>({
    resolver: zodResolver(droneSchema),
    defaultValues: {
      drone_manufacturer: formData.drone_manufacturer ?? '',
      drone_model: formData.drone_model ?? '',
      drone_serial_number: formData.drone_serial_number ?? '',
      flight_date: formData.flight_date ?? '',
    },
  })

  const watchManufacturer = watch('drone_manufacturer')
  const watchSerial = watch('drone_serial_number')
  const models = DRONE_MODELS[watchManufacturer] ?? []
  const isOther = watchManufacturer === 'Autre'

  const serialValid = watchSerial && watchSerial.length >= 3
  const serialTouched = watchSerial !== undefined && watchSerial !== ''

  return (
    <form
      ref={formRef}
      onSubmit={handleSubmit(onSubmit)}
      className="space-y-6 p-6"
    >
      <h2 className="text-lg font-semibold text-white">Informations sur le drone</h2>

      {/* Fabricant */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-1.5">
          Fabricant <span className="text-red-400">*</span>
        </label>
        <select
          {...register('drone_manufacturer')}
          className="w-full rounded-lg bg-[#2a2a2a] border border-gray-600 text-white px-3 py-2.5 text-sm focus:outline-none focus:border-amber-500 transition-colors"
        >
          <option value="">-- Sélectionner un fabricant --</option>
          {MANUFACTURERS.map((m) => (
            <option key={m} value={m}>{m}</option>
          ))}
        </select>
        {errors.drone_manufacturer && (
          <p className="mt-1 text-xs text-red-400">{errors.drone_manufacturer.message}</p>
        )}
      </div>

      {/* Modèle */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-1.5">
          Modèle <span className="text-red-400">*</span>
        </label>
        {isOther ? (
          <input
            type="text"
            {...register('drone_model')}
            placeholder="Entrez le modèle de votre drone"
            className="w-full rounded-lg bg-[#2a2a2a] border border-gray-600 text-white px-3 py-2.5 text-sm placeholder-gray-500 focus:outline-none focus:border-amber-500 transition-colors"
          />
        ) : (
          <select
            {...register('drone_model')}
            disabled={!watchManufacturer || isOther}
            className="w-full rounded-lg bg-[#2a2a2a] border border-gray-600 text-white px-3 py-2.5 text-sm focus:outline-none focus:border-amber-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <option value="">-- Sélectionner un modèle --</option>
            {models.map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        )}
        {errors.drone_model && (
          <p className="mt-1 text-xs text-red-400">{errors.drone_model.message}</p>
        )}
      </div>

      {/* Numéro de série */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-1.5">
          Numéro de série <span className="text-red-400">*</span>
        </label>
        <div className="relative">
          <input
            type="text"
            {...register('drone_serial_number')}
            placeholder="ex : DJI-2024-XXXXXX"
            className={`
              w-full rounded-lg bg-[#2a2a2a] border px-3 py-2.5 pr-10 text-sm text-white placeholder-gray-500
              focus:outline-none transition-colors
              ${errors.drone_serial_number
                ? 'border-red-500 focus:border-red-500'
                : serialValid
                ? 'border-green-500 focus:border-green-500'
                : 'border-gray-600 focus:border-amber-500'
              }
            `}
          />
          {serialTouched && (
            <span className={`absolute right-3 top-1/2 -translate-y-1/2 text-sm ${serialValid ? 'text-green-400' : 'text-red-400'}`}>
              {serialValid ? '✓' : '✗'}
            </span>
          )}
        </div>
        {errors.drone_serial_number && (
          <p className="mt-1 text-xs text-red-400">{errors.drone_serial_number.message}</p>
        )}
      </div>

      {/* Date de vol */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-1.5">
          Date de vol <span className="text-gray-500">(optionnel)</span>
        </label>
        <input
          type="date"
          {...register('flight_date')}
          className="w-full rounded-lg bg-[#2a2a2a] border border-gray-600 text-white px-3 py-2.5 text-sm focus:outline-none focus:border-amber-500 transition-colors"
        />
      </div>
    </form>
  )
}
