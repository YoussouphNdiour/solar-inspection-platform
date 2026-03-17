import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Dashboard } from './pages/Dashboard'
import { SiteDetail } from './pages/SiteDetail'
import { InspectionDetail } from './pages/InspectionDetail'
import { NotFound } from './pages/NotFound'
import { InspectionList } from './components/InspectionList'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="sites/:siteId" element={<SiteDetail />} />
          <Route path="inspections" element={<div className="p-6"><InspectionList /></div>} />
          <Route path="inspections/:inspectionId" element={<InspectionDetail />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
