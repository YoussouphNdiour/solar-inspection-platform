import React, { useState } from 'react'
import { PanelModuleForm, PanelType } from '../../types/site'

interface Step2Props {
  panels: PanelModuleForm[]
  onPanelsChange: (panels: PanelModuleForm[]) => void
}

const PANEL_TYPE_LABELS: Record<PanelType, string> = {
  mono: 'Monocristallin',
  poly: 'Polycristallin',
  bifacial: 'Bifacial',
  thin_film: 'Couche mince',
}

const emptyPanel = (): Omit<PanelModuleForm, 'panel_count' | 'power_w'> & {
  panel_count: number
  power_w: number
} => ({
  brand: '',
  model: '',
  panel_type: 'mono',
  cell_count: undefined,
  power_w: 0,
  panel_count: 1,
  warranty_start_date: '',
  product_warranty_years: undefined,
  hardware_warranty_years: undefined,
  performance_warranty_years: undefined,
})

const inputClass =
  'bg-gray-800 border border-gray-600 text-white rounded-lg px-3 py-2 w-full focus:outline-none focus:border-amber-500 placeholder-gray-500 text-sm'
const labelClass = 'block text-gray-400 text-xs font-medium mb-1'

export const Step2Panels: React.FC<Step2Props> = ({ panels, onPanelsChange }) => {
  const [form, setForm] = useState<PanelModuleForm>(emptyPanel())
  const [formError, setFormError] = useState<string | null>(null)

  const handleChange = <K extends keyof PanelModuleForm>(
    key: K,
    value: PanelModuleForm[K]
  ) => {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  const handleAdd = () => {
    if (!form.brand.trim()) {
      setFormError('La marque est requise.')
      return
    }
    if (!form.model.trim()) {
      setFormError('Le modèle est requis.')
      return
    }
    if (!form.power_w || form.power_w <= 0) {
      setFormError('La puissance doit être supérieure à 0.')
      return
    }
    if (!form.panel_count || form.panel_count < 1) {
      setFormError('Le nombre de panneaux doit être au moins 1.')
      return
    }
    setFormError(null)
    onPanelsChange([...panels, { ...form }])
    setForm(emptyPanel())
  }

  const handleRemove = (index: number) => {
    onPanelsChange(panels.filter((_, i) => i !== index))
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Left column — form */}
      <div className="bg-[#2a2a2a] rounded-xl p-5 space-y-4">
        <h3 className="text-white font-semibold text-sm">Ajouter un module</h3>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className={labelClass}>Marque</label>
            <input
              className={inputClass}
              placeholder="Ex : JA Solar"
              value={form.brand}
              onChange={(e) => handleChange('brand', e.target.value)}
            />
          </div>
          <div>
            <label className={labelClass}>Modèle</label>
            <input
              className={inputClass}
              placeholder="Ex : JAM72S20"
              value={form.model}
              onChange={(e) => handleChange('model', e.target.value)}
            />
          </div>
        </div>

        <div>
          <label className={labelClass}>Type de panneau</label>
          <select
            className={inputClass}
            value={form.panel_type}
            onChange={(e) => handleChange('panel_type', e.target.value as PanelType)}
          >
            {Object.entries(PANEL_TYPE_LABELS).map(([val, label]) => (
              <option key={val} value={val}>{label}</option>
            ))}
          </select>
        </div>

        <div>
          <label className={labelClass}>Nombre de cellules</label>
          <input
            type="number"
            className={inputClass}
            placeholder="Ex : 72"
            value={form.cell_count ?? ''}
            min={0}
            onChange={(e) =>
              handleChange('cell_count', e.target.value ? parseInt(e.target.value) : undefined)
            }
          />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className={labelClass}>Puissance (W)</label>
            <input
              type="number"
              className={inputClass}
              placeholder="Ex : 450"
              value={form.power_w || ''}
              min={0}
              onChange={(e) => handleChange('power_w', parseFloat(e.target.value) || 0)}
            />
          </div>
          <div>
            <label className={labelClass}>Nombre de panneaux</label>
            <input
              type="number"
              className={inputClass}
              value={form.panel_count}
              min={1}
              onChange={(e) => handleChange('panel_count', parseInt(e.target.value) || 1)}
            />
          </div>
        </div>

        <div>
          <label className={labelClass}>Date début garantie</label>
          <input
            type="date"
            className={inputClass}
            value={form.warranty_start_date ?? ''}
            onChange={(e) => handleChange('warranty_start_date', e.target.value)}
          />
        </div>

        <div className="grid grid-cols-3 gap-2">
          <div>
            <label className={labelClass}>Garantie Produit (ans)</label>
            <input
              type="number"
              className={inputClass}
              placeholder="10"
              value={form.product_warranty_years ?? ''}
              min={0}
              onChange={(e) =>
                handleChange(
                  'product_warranty_years',
                  e.target.value ? parseInt(e.target.value) : undefined
                )
              }
            />
          </div>
          <div>
            <label className={labelClass}>Garantie Matériel (ans)</label>
            <input
              type="number"
              className={inputClass}
              placeholder="10"
              value={form.hardware_warranty_years ?? ''}
              min={0}
              onChange={(e) =>
                handleChange(
                  'hardware_warranty_years',
                  e.target.value ? parseInt(e.target.value) : undefined
                )
              }
            />
          </div>
          <div>
            <label className={labelClass}>Garantie Perf. (ans)</label>
            <input
              type="number"
              className={inputClass}
              placeholder="25"
              value={form.performance_warranty_years ?? ''}
              min={0}
              onChange={(e) =>
                handleChange(
                  'performance_warranty_years',
                  e.target.value ? parseInt(e.target.value) : undefined
                )
              }
            />
          </div>
        </div>

        {formError && <p className="text-red-400 text-xs">{formError}</p>}

        <button
          type="button"
          onClick={handleAdd}
          className="w-full bg-amber-500 hover:bg-amber-600 text-black font-semibold rounded-lg py-2 text-sm transition-colors"
        >
          Ajouter +
        </button>
      </div>

      {/* Right column — list */}
      <div>
        <h3 className="text-white font-semibold text-sm mb-3">
          Panneaux ajoutés ({panels.length})
        </h3>

        {panels.length === 0 ? (
          <div className="bg-[#2a2a2a] rounded-xl p-6 text-center text-gray-500 text-sm">
            Aucun panneau ajouté
          </div>
        ) : (
          <div className="space-y-3">
            {panels.map((panel, index) => (
              <div
                key={index}
                className="bg-[#2a2a2a] rounded-xl p-4 flex items-start justify-between gap-3"
              >
                <div className="flex-1 min-w-0">
                  <p className="text-white font-semibold text-sm">
                    {panel.brand} — {panel.model}
                  </p>
                  <p className="text-gray-400 text-xs mt-0.5">
                    {PANEL_TYPE_LABELS[panel.panel_type]} · {panel.power_w} W · {panel.panel_count} panneaux
                  </p>
                  {panel.warranty_start_date && (
                    <p className="text-gray-500 text-xs">
                      Garantie depuis {panel.warranty_start_date}
                    </p>
                  )}
                </div>
                <button
                  type="button"
                  onClick={() => handleRemove(index)}
                  className="text-red-400 hover:text-red-300 text-xl font-bold flex-shrink-0"
                  title="Supprimer ce panneau"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
