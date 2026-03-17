import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Dashboard } from './pages/Dashboard'
import { SiteDetail } from './pages/SiteDetail'
import { MalicoundaDemo } from './pages/MalicoundaDemo'
import { NotFound } from './pages/NotFound'
import { InspectionList } from './components/InspectionList'
import { NewSitePage } from './pages/sites/NewSitePage'
import { NewInspectionPage } from './pages/inspections/NewInspectionPage'
import { InspectionDetailPage } from './pages/inspections/InspectionDetailPage'
import { UploadPhotosPage } from './pages/inspections/UploadPhotosPage'
import { ReportDetailPage } from './pages/reports/ReportDetailPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="sites/new" element={<NewSitePage />} />
          <Route path="sites/:siteId" element={<SiteDetail />} />
          <Route path="inspections" element={<div className="p-6"><InspectionList /></div>} />
          <Route path="inspections/new" element={<NewInspectionPage />} />
          <Route path="inspections/:inspectionId" element={<InspectionDetailPage />} />
          <Route path="inspections/:inspectionId/upload" element={<UploadPhotosPage />} />
          <Route path="upload" element={<UploadPhotosPage />} />
          <Route path="reports/:inspectionId" element={<ReportDetailPage />} />
          <Route path="demo/malicounda" element={<MalicoundaDemo />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
