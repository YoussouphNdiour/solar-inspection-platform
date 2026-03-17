import React from 'react'
import { SiteWizard } from '../../components/wizard/SiteWizard'

export const NewSitePage: React.FC = () => (
  <div className="min-h-full bg-[#1a1a1a] p-6">
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-white mb-6">Nouvelle centrale électrique</h1>
      <SiteWizard />
    </div>
  </div>
)
