import React, { useState } from 'react'
import { BosComponentForm, BosComponentType } from '../../types/site'

interface Step3Props {
  components: BosComponentForm[]
  onComponentsChange: (components: BosComponentForm[]) => void
}

const COMPONENT_TYPE_LABELS: Record<BosComponentType, string> = {
  inverter: 'Onduleur',
  combiner_box: 'Boîte de combinaison',
  cable: 'Câble',
  mounting: 'Montage',
  monitoring: 'Monitoring',
}

const emptyComponent = (): BosComponentForm => ({
  component_type: 'inverter',
  brand: '',
  model: '',
  quantity: 1,
})

const inputClass =
  'bg-gray-800 border border-gray-600 text-white rounded-lg px-3 py-2 w-full focus:outline-none focus:border-amber-500 placeholder-gray-500 text-sm'
const labelClass = 'block text-gray-400 text-xs font-medium mb-1'

export const Step3BOS: React.FC<Step3Props> = ({ components, onComponentsChange }) => {
  const [form, setForm] = useState<BosComponentForm>(emptyComponent())
  const [formError, setFormError] = useState<string | null>(null)

  const handleChange = <K extends keyof BosComponentForm>(
    key: K,
    value: BosComponentForm[K]
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
    if (!form.quantity || form.quantity < 1) {
      setFormError('La quantité doit être au moins 1.')
      return
    }
    setFormError(null)
    onComponentsChange([...components, { ...form }])
    setForm(emptyComponent())
  }

  const handleRemove = (index: number) => {
    onComponentsChange(components.filter((_, i) => i !== index))
  }

  return (
    <div className="space-y-6">
      {/* Note */}
      <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg px-4 py-3">
        <p className="text-amber-400 text-sm">
          ℹ️ Les composants BOS sont optionnels mais recommandés pour un rapport complet.
        </p>
      </div>

      {/* Horizontal form */}
      <div className="bg-[#2a2a2a] rounded-xl p-5">
        <h3 className="text-white font-semibold text-sm mb-4">Ajouter un composant</h3>

        <div className="grid grid-cols-1 sm:grid-cols-5 gap-3 items-end">
          <div>
            <label className={labelClass}>Type de composant</label>
            <select
              className={inputClass}
              value={form.component_type}
              onChange={(e) => handleChange('component_type', e.target.value as BosComponentType)}
            >
              {Object.entries(COMPONENT_TYPE_LABELS).map(([val, label]) => (
                <option key={val} value={val}>{label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className={labelClass}>Marque</label>
            <input
              className={inputClass}
              placeholder="Ex : SMA"
              value={form.brand}
              onChange={(e) => handleChange('brand', e.target.value)}
            />
          </div>

          <div>
            <label className={labelClass}>Modèle</label>
            <input
              className={inputClass}
              placeholder="Ex : Sunny Tripower"
              value={form.model}
              onChange={(e) => handleChange('model', e.target.value)}
            />
          </div>

          <div>
            <label className={labelClass}>Quantité</label>
            <input
              type="number"
              className={inputClass}
              value={form.quantity}
              min={1}
              onChange={(e) => handleChange('quantity', parseInt(e.target.value) || 1)}
            />
          </div>

          <div>
            <button
              type="button"
              onClick={handleAdd}
              className="w-full bg-amber-500 hover:bg-amber-600 text-black font-semibold rounded-lg py-2 text-sm transition-colors"
            >
              Ajouter
            </button>
          </div>
        </div>

        {formError && <p className="text-red-400 text-xs mt-2">{formError}</p>}
      </div>

      {/* Components table */}
      {components.length > 0 ? (
        <div className="bg-[#2a2a2a] rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left text-gray-400 font-medium px-4 py-3">Type</th>
                <th className="text-left text-gray-400 font-medium px-4 py-3">Marque</th>
                <th className="text-left text-gray-400 font-medium px-4 py-3">Modèle</th>
                <th className="text-center text-gray-400 font-medium px-4 py-3">Quantité</th>
                <th className="text-center text-gray-400 font-medium px-4 py-3">Supprimer</th>
              </tr>
            </thead>
            <tbody>
              {components.map((comp, index) => (
                <tr key={index} className="border-b border-gray-700/50 hover:bg-gray-800/30">
                  <td className="px-4 py-3 text-white">
                    {COMPONENT_TYPE_LABELS[comp.component_type]}
                  </td>
                  <td className="px-4 py-3 text-gray-300">{comp.brand}</td>
                  <td className="px-4 py-3 text-gray-300">{comp.model}</td>
                  <td className="px-4 py-3 text-center text-gray-300">{comp.quantity}</td>
                  <td className="px-4 py-3 text-center">
                    <button
                      type="button"
                      onClick={() => handleRemove(index)}
                      className="text-red-400 hover:text-red-300 text-lg font-bold"
                      title="Supprimer ce composant"
                    >
                      ×
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="bg-[#2a2a2a] rounded-xl p-6 text-center text-gray-500 text-sm">
          Aucun composant BOS ajouté
        </div>
      )}
    </div>
  )
}
