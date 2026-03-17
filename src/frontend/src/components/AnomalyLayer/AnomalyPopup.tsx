import type { AnomalyProperties, CoAClass } from '../../types'

const COA_COLORS: Record<CoAClass, string> = {
  CoA1: 'text-yellow-700 bg-yellow-50 border-yellow-300',
  CoA2: 'text-orange-700 bg-orange-50 border-orange-300',
  CoA3: 'text-red-700 bg-red-50 border-red-300',
}

const ANOMALY_LABELS: Record<string, string> = {
  hotspot_cellule: 'Hotspot cellule',
  bypass_diode: 'Bypass diode',
  pid: 'PID',
  string_ouverte: 'String ouverte',
  ombrage: 'Ombrage',
  salissure: 'Salissure',
}

interface Props {
  properties: AnomalyProperties
  onClose: () => void
}

export const AnomalyPopup: React.FC<Props> = ({ properties, onClose }) => {
  const coaClass = properties.coa_class as CoAClass

  return (
    <div className="bg-white rounded-lg shadow-lg p-4 min-w-52 text-sm">
      <div className="flex justify-between items-center mb-3">
        <span className={`px-2 py-0.5 rounded text-xs font-bold border ${COA_COLORS[coaClass]}`}>
          {properties.coa_class}
        </span>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 text-lg leading-none"
        >
          ×
        </button>
      </div>

      <p className="font-medium text-gray-800">{properties.panel_id}</p>
      <p className="text-gray-500 mt-1">
        {ANOMALY_LABELS[properties.anomaly_type] || properties.anomaly_type}
      </p>

      <div className="mt-3 space-y-1 text-xs text-gray-600">
        <div className="flex justify-between">
          <span>ΔT mesuré</span>
          <span className="font-mono">{properties.delta_t_measured.toFixed(1)}°C</span>
        </div>
        <div className="flex justify-between">
          <span>ΔT norm. (1000W/m²)</span>
          <span className="font-mono font-semibold">{properties.delta_t_normalized.toFixed(1)}°C</span>
        </div>
        <div className="flex justify-between">
          <span>Confiance</span>
          <span className="font-mono">{(properties.confidence * 100).toFixed(0)}%</span>
        </div>
      </div>
    </div>
  )
}
