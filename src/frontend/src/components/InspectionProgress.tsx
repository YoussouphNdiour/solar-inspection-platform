import React from 'react'
import type { ProgressStep } from '../types/inspection'

interface Props {
  steps: ProgressStep[]
  currentStep: number
  onStepClick?: (step: number) => void
}

// Les 5 étapes :
// 0: 💳 Paiement
// 1: ⬆️ Téléchargement
// 2: 👁️ Évaluation
// 3: 📊 Analyse
// 4: 📄 Rapport

export const DEFAULT_STEPS: ProgressStep[] = [
  { step: 0, label: 'Paiement', icon: '💳', state: 'active' },
  { step: 1, label: 'Téléchargement', icon: '⬆️', state: 'locked' },
  { step: 2, label: 'Évaluation', icon: '👁️', state: 'locked' },
  { step: 3, label: 'Analyse', icon: '📊', state: 'locked' },
  { step: 4, label: 'Rapport', icon: '📄', state: 'locked' },
]

export const InspectionProgress: React.FC<Props> = ({ steps, currentStep, onStepClick }) => {
  const percentage = (currentStep / 4) * 100

  return (
    <div className="w-full">
      {/* Barre linéaire */}
      <div className="h-1.5 bg-gray-700 rounded-full mb-6 overflow-hidden">
        <div
          className="h-full bg-amber-500 rounded-full transition-all duration-500"
          style={{ width: `${percentage}%` }}
        />
      </div>

      {/* Étapes avec icônes */}
      <div className="flex justify-between">
        {steps.map((step) => {
          const isClickable = step.state === 'completed' && onStepClick
          return (
            <div
              key={step.step}
              className={`flex flex-col items-center gap-1 ${isClickable ? 'cursor-pointer' : ''}`}
              onClick={() => isClickable && onStepClick(step.step)}
            >
              {/* Cercle icône */}
              <div
                className={`
                  w-10 h-10 rounded-full flex items-center justify-center text-lg border-2 transition-all
                  ${step.state === 'completed' ? 'bg-amber-500 border-amber-500 text-black' : ''}
                  ${step.state === 'active' ? 'bg-[#2a2a2a] border-amber-500 text-amber-500' : ''}
                  ${step.state === 'locked' ? 'bg-[#2a2a2a] border-gray-600 text-gray-600' : ''}
                `}
              >
                {step.state === 'completed' ? '✓' : step.icon}
              </div>
              {/* Label */}
              <span
                className={`text-xs font-medium text-center ${
                  step.state === 'locked'
                    ? 'text-gray-600'
                    : step.state === 'active'
                    ? 'text-amber-500'
                    : 'text-gray-300'
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
}
