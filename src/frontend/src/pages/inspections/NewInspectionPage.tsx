import React from 'react'
import { InspectionWizard } from '../../components/wizard/InspectionWizard'

export const NewInspectionPage: React.FC = () => (
  <div className="min-h-full bg-[#1a1a1a] p-6">
    <div className="max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold text-white mb-2">Nouvel Examen</h1>
      <p className="text-gray-400 mb-6">
        Créez un nouvel examen d'inspection drone pour votre centrale solaire.
      </p>
      <InspectionWizard />
    </div>
  </div>
)
