import React from 'react'
import { UseFormRegister, FieldErrors, Controller, Control } from 'react-hook-form'
import { SiteFormData, SiteType } from '../../types/site'
import { FileDropZone } from '../ui/FileDropZone'

interface Step1Props {
  register: UseFormRegister<SiteFormData>
  errors: FieldErrors<SiteFormData>
  control: Control<SiteFormData>
  watchSiteType: SiteType
  onSiteTypeChange: (type: SiteType) => void
}

const SITE_TYPE_OPTIONS = [
  {
    value: 'ground' as SiteType,
    icon: '🏭',
    title: 'Terre Solaire',
    description: 'Projets ouverts à grande échelle',
    disabled: false,
  },
  {
    value: 'rooftop' as SiteType,
    icon: '🏢',
    title: 'Toit Solaire',
    description: 'Bâtiments et usines commerciaux',
    disabled: false,
  },
  {
    value: 'residential' as SiteType,
    icon: '🏠',
    title: 'Solaire résidentiel',
    description: 'Maisons et petites entreprises',
    disabled: false,
  },
  {
    value: 'floating' as SiteType,
    icon: '🚢',
    title: 'Centrale flottante',
    description: "Installation à la surface de l'eau",
    disabled: true,
  },
]

const COUNTRIES = [
  'Sénégal', 'France', 'Maroc', 'Côte d\'Ivoire', 'Mali', 'Burkina Faso',
  'Niger', 'Guinée', 'Cameroun', 'Madagascar', 'Tunisie', 'Algérie', 'Égypte',
  'Afrique du Sud', 'Kenya', 'Nigéria', 'Ghana', 'Éthiopie', 'Tanzanie',
  'Allemagne', 'Espagne', 'Italie', 'Pays-Bas', 'Belgique', 'Suisse',
  'Canada', 'États-Unis', 'Brésil', 'Inde', 'Chine', 'Japon', 'Australie',
]

const inputClass =
  'bg-gray-800 border border-gray-600 text-white rounded-lg px-3 py-2 w-full focus:outline-none focus:border-amber-500 placeholder-gray-500 text-sm'
const labelClass = 'block text-gray-400 text-xs font-medium mb-1'
const errorClass = 'text-red-400 text-xs mt-1'

export const Step1BasicInfo: React.FC<Step1Props> = ({
  register,
  errors,
  control,
  watchSiteType,
  onSiteTypeChange,
}) => {
  return (
    <div className="space-y-6">
      {/* Site Type Selection */}
      <div>
        <p className="text-white font-semibold mb-3">Type de centrale *</p>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {SITE_TYPE_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              type="button"
              disabled={opt.disabled}
              onClick={() => !opt.disabled && onSiteTypeChange(opt.value)}
              className={`
                relative flex flex-col items-center text-center p-4 rounded-xl border-2 transition-all
                bg-[#2a2a2a]
                ${opt.disabled ? 'opacity-50 cursor-not-allowed border-gray-700' : 'cursor-pointer hover:border-amber-400'}
                ${watchSiteType === opt.value && !opt.disabled ? 'border-amber-500' : 'border-gray-700'}
              `}
            >
              {opt.disabled && (
                <span className="absolute top-2 right-2 bg-amber-500 text-black text-[10px] font-bold px-1.5 py-0.5 rounded-full">
                  Bientôt
                </span>
              )}
              <span className="text-3xl mb-2">{opt.icon}</span>
              <span className="text-white text-xs font-semibold">{opt.title}</span>
              <span className="text-gray-400 text-[11px] mt-1">{opt.description}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Form Fields */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Nom */}
        <div className="sm:col-span-2">
          <label className={labelClass}>Nom *</label>
          <input
            {...register('name')}
            className={inputClass}
            placeholder="Ex : Centrale solaire de Malicounda"
          />
          {errors.name && <p className={errorClass}>{errors.name.message}</p>}
        </div>

        {/* Date de fondation */}
        <div>
          <label className={labelClass}>Date de fondation *</label>
          <input
            type="date"
            {...register('installation_date')}
            className={inputClass}
          />
          {errors.installation_date && (
            <p className={errorClass}>{errors.installation_date.message}</p>
          )}
        </div>

        {/* Type de montage */}
        <div>
          <label className={labelClass}>Type de montage *</label>
          <select {...register('mounting_type')} className={inputClass}>
            <option value="fixed">Montage fixe</option>
            <option value="tracker_single_axis">Tracker axe simple</option>
            <option value="tracker_dual_axis">Tracker 2 axes</option>
          </select>
          {errors.mounting_type && (
            <p className={errorClass}>{errors.mounting_type.message}</p>
          )}
        </div>

        {/* Angle du panneau */}
        <div>
          <label className={labelClass}>Angle du panneau (°) *</label>
          <div className="relative">
            <input
              type="number"
              {...register('tilt_angle_deg', { valueAsNumber: true })}
              className={inputClass + ' pr-8'}
              defaultValue={30}
              min={0}
              max={90}
            />
            <span className="absolute right-3 top-2 text-gray-400 text-sm">°</span>
          </div>
          {errors.tilt_angle_deg && (
            <p className={errorClass}>{errors.tilt_angle_deg.message}</p>
          )}
        </div>

        {/* Azimut — direction + degrés */}
        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className={labelClass}>Direction azimut *</label>
            <select {...register('azimuth_direction')} className={inputClass}>
              {['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'].map((d) => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
            {errors.azimuth_direction && (
              <p className={errorClass}>{errors.azimuth_direction.message}</p>
            )}
          </div>
          <div>
            <label className={labelClass}>Azimut (0-360°) *</label>
            <input
              type="number"
              {...register('azimuth_degrees', { valueAsNumber: true })}
              className={inputClass}
              min={0}
              max={360}
              placeholder="180"
            />
            {errors.azimuth_degrees && (
              <p className={errorClass}>{errors.azimuth_degrees.message}</p>
            )}
          </div>
        </div>

        {/* Puissance DC */}
        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className={labelClass}>Puissance DC *</label>
            <input
              type="number"
              {...register('dc_power_installed_kw', { valueAsNumber: true })}
              className={inputClass}
              placeholder="1000"
              min={0}
              step={0.1}
            />
            {errors.dc_power_installed_kw && (
              <p className={errorClass}>{errors.dc_power_installed_kw.message}</p>
            )}
          </div>
          <div>
            <label className={labelClass}>Unité</label>
            <select {...register('dc_power_unit')} className={inputClass}>
              <option value="kW">kW</option>
              <option value="MW">MW</option>
            </select>
          </div>
        </div>

        {/* Prix de vente */}
        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className={labelClass}>Prix de vente kW *</label>
            <input
              type="number"
              {...register('energy_sale_price', { valueAsNumber: true })}
              className={inputClass}
              placeholder="0.08"
              min={0}
              step={0.001}
            />
            {errors.energy_sale_price && (
              <p className={errorClass}>{errors.energy_sale_price.message}</p>
            )}
          </div>
          <div>
            <label className={labelClass}>Devise</label>
            <select {...register('currency')} className={inputClass}>
              <option value="USD">USD</option>
              <option value="XOF">XOF</option>
              <option value="EUR">EUR</option>
              <option value="MAD">MAD</option>
            </select>
          </div>
        </div>

        {/* Adresse Ligne 1 */}
        <div className="sm:col-span-2">
          <label className={labelClass}>Adresse Ligne 1 *</label>
          <input
            {...register('address_line1')}
            className={inputClass}
            placeholder="Route nationale, Zone industrielle..."
          />
          {errors.address_line1 && (
            <p className={errorClass}>{errors.address_line1.message}</p>
          )}
        </div>

        {/* Adresse Ligne 2 */}
        <div className="sm:col-span-2">
          <label className={labelClass}>Adresse Ligne 2 (optionnel)</label>
          <input
            {...register('address_line2')}
            className={inputClass}
            placeholder="Complément d'adresse"
          />
        </div>

        {/* District */}
        <div>
          <label className={labelClass}>District *</label>
          <input
            {...register('district')}
            className={inputClass}
            placeholder="Mbour"
          />
          {errors.district && <p className={errorClass}>{errors.district.message}</p>}
        </div>

        {/* Ville */}
        <div>
          <label className={labelClass}>Ville *</label>
          <input
            {...register('city')}
            className={inputClass}
            placeholder="Malicounda"
          />
          {errors.city && <p className={errorClass}>{errors.city.message}</p>}
        </div>

        {/* État / Province */}
        <div>
          <label className={labelClass}>État / Province (optionnel)</label>
          <input
            {...register('state_province')}
            className={inputClass}
            placeholder="Thiès"
          />
        </div>

        {/* Pays */}
        <div>
          <label className={labelClass}>Pays *</label>
          <select {...register('country')} className={inputClass}>
            <option value="">-- Sélectionner --</option>
            {COUNTRIES.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
          {errors.country && <p className={errorClass}>{errors.country.message}</p>}
        </div>

        {/* Latitude */}
        <div>
          <label className={labelClass}>Latitude *</label>
          <input
            type="number"
            {...register('latitude', { valueAsNumber: true })}
            className={inputClass}
            placeholder="14.3456"
            step={0.000001}
          />
          {errors.latitude && <p className={errorClass}>{errors.latitude.message}</p>}
        </div>

        {/* Longitude */}
        <div>
          <label className={labelClass}>Longitude *</label>
          <input
            type="number"
            {...register('longitude', { valueAsNumber: true })}
            className={inputClass}
            placeholder="-16.7890"
            step={0.000001}
          />
          {errors.longitude && <p className={errorClass}>{errors.longitude.message}</p>}
        </div>

        {/* Code Postal */}
        <div>
          <label className={labelClass}>Code Postal</label>
          <input
            {...register('postal_code')}
            className={inputClass}
            placeholder="21000"
          />
        </div>

        {/* Plan d'aménagement */}
        <div className="sm:col-span-2">
          <label className={labelClass}>Plan d'aménagement (optionnel)</label>
          <Controller
            name="kml_file"
            control={control}
            render={({ field }) => (
              <FileDropZone
                onFileChange={(file) => field.onChange(file)}
                value={field.value as File | null}
              />
            )}
          />
        </div>
      </div>
    </div>
  )
}
