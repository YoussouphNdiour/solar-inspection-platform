import React from 'react'
import { SiteFormData, PanelModuleForm, BosComponentForm } from '../../types/site'

interface Step4Props {
  formData: SiteFormData
  onSubmit: () => void
  isSubmitting: boolean
}

const SITE_TYPE_LABELS: Record<string, string> = {
  ground: 'Terre Solaire',
  rooftop: 'Toit Solaire',
  residential: 'Solaire résidentiel',
  floating: 'Centrale flottante',
}

const PANEL_TYPE_LABELS: Record<string, string> = {
  mono: 'Monocristallin',
  poly: 'Polycristallin',
  bifacial: 'Bifacial',
  thin_film: 'Couche mince',
}

const BOS_TYPE_LABELS: Record<string, string> = {
  inverter: 'Onduleur',
  combiner_box: 'Boîte de combinaison',
  cable: 'Câble',
  mounting: 'Montage',
  monitoring: 'Monitoring',
}

const SectionCard: React.FC<{ title: string; children: React.ReactNode }> = ({
  title,
  children,
}) => (
  <div className="bg-[#2a2a2a] rounded-xl p-5">
    <h3 className="text-amber-500 font-semibold text-sm uppercase tracking-wide mb-4">
      {title}
    </h3>
    {children}
  </div>
)

const InfoRow: React.FC<{ label: string; value?: string | number | null }> = ({ label, value }) => (
  <div className="flex justify-between items-start gap-4 py-1.5 border-b border-gray-700/50 last:border-0">
    <span className="text-gray-400 text-sm flex-shrink-0">{label}</span>
    <span className="text-white text-sm text-right">{value ?? '—'}</span>
  </div>
)

export const Step4Confirm: React.FC<Step4Props> = ({ formData, onSubmit, isSubmitting }) => {
  const totalPanels = formData.panels.reduce((sum, p) => sum + p.panel_count, 0)

  const fullAddress = [
    formData.address_line1,
    formData.address_line2,
    formData.district,
    formData.city,
    formData.state_province,
    formData.postal_code,
    formData.country,
  ]
    .filter(Boolean)
    .join(', ')

  return (
    <div className="space-y-5">
      {/* General info */}
      <SectionCard title="Informations générales">
        <InfoRow label="Nom" value={formData.name} />
        <InfoRow label="Type de centrale" value={SITE_TYPE_LABELS[formData.site_type]} />
        <InfoRow
          label="Puissance DC"
          value={`${formData.dc_power_installed_kw} ${formData.dc_power_unit}`}
        />
        <InfoRow
          label="Date de fondation"
          value={formData.installation_date}
        />
        <InfoRow
          label="Prix de vente"
          value={`${formData.energy_sale_price} ${formData.currency}/kWh`}
        />
        <InfoRow label="Type de montage" value={formData.mounting_type} />
        <InfoRow label="Angle du panneau" value={`${formData.tilt_angle_deg}°`} />
        <InfoRow
          label="Azimut"
          value={`${formData.azimuth_direction} (${formData.azimuth_degrees}°)`}
        />
      </SectionCard>

      {/* Location */}
      <SectionCard title="Localisation">
        <InfoRow label="Adresse" value={fullAddress} />
        <InfoRow label="Latitude" value={formData.latitude} />
        <InfoRow label="Longitude" value={formData.longitude} />
        {formData.kml_file && (
          <InfoRow label="Fichier plan" value={formData.kml_file.name} />
        )}
      </SectionCard>

      {/* Panels */}
      <SectionCard title={`Modules (${totalPanels} panneaux)`}>
        {formData.panels.length === 0 ? (
          <p className="text-gray-500 text-sm">Aucun module défini</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-700">
                  <th className="text-left text-gray-400 font-medium py-2 pr-4">Marque / Modèle</th>
                  <th className="text-left text-gray-400 font-medium py-2 pr-4">Type</th>
                  <th className="text-right text-gray-400 font-medium py-2 pr-4">Puissance</th>
                  <th className="text-right text-gray-400 font-medium py-2">Qté</th>
                </tr>
              </thead>
              <tbody>
                {formData.panels.map((panel: PanelModuleForm, i: number) => (
                  <tr key={i} className="border-b border-gray-700/50">
                    <td className="text-white py-2 pr-4">
                      {panel.brand} {panel.model}
                    </td>
                    <td className="text-gray-300 py-2 pr-4">
                      {PANEL_TYPE_LABELS[panel.panel_type]}
                    </td>
                    <td className="text-gray-300 py-2 pr-4 text-right">{panel.power_w} W</td>
                    <td className="text-gray-300 py-2 text-right">{panel.panel_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </SectionCard>

      {/* BOS */}
      <SectionCard title={`Composants BOS (${formData.bos_components.length})`}>
        {formData.bos_components.length === 0 ? (
          <p className="text-gray-500 text-sm">Aucun composant BOS défini</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-700">
                  <th className="text-left text-gray-400 font-medium py-2 pr-4">Type</th>
                  <th className="text-left text-gray-400 font-medium py-2 pr-4">Marque / Modèle</th>
                  <th className="text-right text-gray-400 font-medium py-2">Quantité</th>
                </tr>
              </thead>
              <tbody>
                {formData.bos_components.map((comp: BosComponentForm, i: number) => (
                  <tr key={i} className="border-b border-gray-700/50">
                    <td className="text-white py-2 pr-4">
                      {BOS_TYPE_LABELS[comp.component_type]}
                    </td>
                    <td className="text-gray-300 py-2 pr-4">
                      {comp.brand} {comp.model}
                    </td>
                    <td className="text-gray-300 py-2 text-right">{comp.quantity}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </SectionCard>

      {/* Submit button */}
      <button
        type="button"
        onClick={onSubmit}
        disabled={isSubmitting}
        className="w-full bg-amber-500 hover:bg-amber-600 disabled:opacity-50 disabled:cursor-not-allowed text-black font-bold rounded-xl py-4 text-lg transition-colors"
      >
        {isSubmitting ? '⏳ Création en cours...' : '🚀 Créer la centrale'}
      </button>
    </div>
  )
}
