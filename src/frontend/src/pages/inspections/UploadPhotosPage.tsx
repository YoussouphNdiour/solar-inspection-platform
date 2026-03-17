import React, { useState, useCallback, useRef, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { inspectionsApi } from '../../api/inspections'
import type { InspectionResponse } from '../../types/inspection'

// ─── Types ────────────────────────────────────────────────────────────────────

interface FileItem {
  id: string
  file: File
  type: 'rgb' | 'thermal'
  previewUrl?: string
  uploaded: boolean
  error?: string
}

type Step = 1 | 2 | 3

// ─── Helpers ──────────────────────────────────────────────────────────────────

function detectType(filename: string): 'rgb' | 'thermal' {
  const upper = filename.toUpperCase()
  if (
    upper.includes('_T.') ||
    upper.includes('_THERMAL') ||
    upper.includes('_IR.') ||
    upper.includes('_T_')
  ) {
    return 'thermal'
  }
  return 'rgb'
}

function isImageFile(file: File): boolean {
  return file.type.startsWith('image/') || /\.(jpg|jpeg|tif|tiff|rjpeg)$/i.test(file.name)
}

function truncate(name: string, max = 18): string {
  if (name.length <= max) return name
  const ext = name.lastIndexOf('.')
  const base = ext > 0 ? name.slice(0, ext) : name
  const suffix = ext > 0 ? name.slice(ext) : ''
  return base.slice(0, max - suffix.length - 3) + '…' + suffix
}

// ─── Step indicator ───────────────────────────────────────────────────────────

const StepIndicator: React.FC<{ current: Step }> = ({ current }) => {
  const steps = [
    { n: 1 as Step, label: 'Sélection centrale' },
    { n: 2 as Step, label: 'Upload photos' },
    { n: 3 as Step, label: 'Confirmation' },
  ]
  return (
    <div className="flex items-center gap-0 mb-8">
      {steps.map(({ n, label }, i) => (
        <React.Fragment key={n}>
          <div className="flex flex-col items-center gap-1">
            <div
              className={`w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold border-2 transition-colors ${
                current === n
                  ? 'bg-amber-500 border-amber-500 text-black'
                  : current > n
                  ? 'bg-green-600 border-green-600 text-white'
                  : 'bg-[#2a2a2a] border-gray-600 text-gray-500'
              }`}
            >
              {current > n ? '✓' : n}
            </div>
            <span
              className={`text-xs whitespace-nowrap ${
                current === n ? 'text-amber-400' : current > n ? 'text-green-400' : 'text-gray-500'
              }`}
            >
              {label}
            </span>
          </div>
          {i < steps.length - 1 && (
            <div
              className={`h-0.5 flex-1 mx-2 mb-5 transition-colors ${
                current > n ? 'bg-green-600' : 'bg-gray-700'
              }`}
            />
          )}
        </React.Fragment>
      ))}
    </div>
  )
}

// ─── Step 1 — Inspection selector ─────────────────────────────────────────────

interface Step1Props {
  preselectedId: string | null
  onSelect: (id: string) => void
}

const Step1: React.FC<Step1Props> = ({ preselectedId, onSelect }) => {
  const [inspections, setInspections] = useState<InspectionResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)
  const [clickedPending, setClickedPending] = useState<string | null>(null)

  useEffect(() => {
    inspectionsApi
      .list()
      .then(setInspections)
      .catch(() => setErrorMsg('Impossible de charger les inspections.'))
      .finally(() => setLoading(false))
  }, [])

  // Auto-select if preselected id is provided and payment is ok
  useEffect(() => {
    if (preselectedId && inspections.length > 0) {
      const match = inspections.find((i) => i.id === preselectedId)
      if (match && match.payment_status === 'paid') {
        onSelect(preselectedId)
      }
    }
  }, [preselectedId, inspections, onSelect])

  if (loading)
    return <div className="text-gray-400 py-12 text-center animate-pulse">Chargement des inspections…</div>
  if (errorMsg)
    return <div className="text-red-400 py-8 text-center">{errorMsg}</div>

  if (inspections.length === 0)
    return (
      <div className="text-center py-16 text-gray-500">
        <p className="text-4xl mb-3">📋</p>
        <p className="text-lg font-semibold text-gray-300 mb-1">Aucune inspection trouvée</p>
        <p className="text-sm">Créez d'abord une inspection avant d'uploader des photos.</p>
      </div>
    )

  function getBadge(insp: InspectionResponse) {
    if (insp.payment_status === 'pending') {
      return <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-red-900 text-red-300 border border-red-700">💳 Paiement en attente</span>
    }
    if (insp.status === 'created') {
      return <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-green-900 text-green-300 border border-green-700">✅ Prêt pour upload</span>
    }
    if (insp.status === 'images_uploaded') {
      return <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-blue-900 text-blue-300 border border-blue-700">📤 Images uploadées</span>
    }
    if (insp.status === 'processing') {
      return <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-orange-900 text-orange-300 border border-orange-700">⚙️ En traitement</span>
    }
    return <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-gray-700 text-gray-300">{insp.status}</span>
  }

  return (
    <div className="space-y-3">
      <p className="text-gray-400 text-sm mb-4">
        Sélectionnez l'inspection pour laquelle vous souhaitez uploader des photos.
      </p>
      {inspections.map((insp) => {
        const isPending = insp.payment_status === 'pending'
        const isSelected = insp.id === preselectedId
        return (
          <div
            key={insp.id}
            onClick={() => {
              if (isPending) {
                setClickedPending(insp.id)
                return
              }
              onSelect(insp.id)
            }}
            className={`relative rounded-xl border p-4 transition-all cursor-pointer ${
              isPending
                ? 'bg-[#1e1e1e] border-gray-700 opacity-60 cursor-not-allowed'
                : isSelected
                ? 'bg-[#2a2a2a] border-amber-500 ring-1 ring-amber-500'
                : 'bg-[#2a2a2a] border-gray-700 hover:border-amber-500/50 hover:bg-[#2f2f2f]'
            }`}
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <p className="text-white font-semibold truncate">
                    {insp.site_name ?? `Inspection #${insp.id.slice(0, 8)}`}
                  </p>
                  {getBadge(insp)}
                </div>
                <p className="text-gray-400 text-sm mt-1">
                  {new Date(insp.created_at).toLocaleDateString('fr-FR', {
                    day: '2-digit', month: 'long', year: 'numeric',
                  })}
                  {' · '}
                  {insp.plan_type === 'professional_5gsd' ? 'Professional 5 GSD' : 'Enterprise 3 GSD'}
                </p>
              </div>
              <div className="flex-shrink-0 text-right">
                <p className="text-xs text-gray-500 font-mono">
                  RGB: — | Thermique: — | Total: 0
                </p>
              </div>
            </div>
            {clickedPending === insp.id && isPending && (
              <div className="mt-3 flex items-center gap-2 text-red-400 text-sm bg-red-950/50 rounded-lg px-3 py-2">
                ❌ Impossible — paiement en attente. Complétez le paiement d'abord.
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

// ─── Step 2 — Upload zone ──────────────────────────────────────────────────────

interface Step2Props {
  files: FileItem[]
  uploading: boolean
  uploadProgress: number
  uploadedCount: number
  onFilesAdded: (newFiles: File[]) => void
  onRemoveFile: (id: string) => void
  onToggleType: (id: string) => void
  onUpload: () => void
}

const Step2: React.FC<Step2Props> = ({
  files,
  uploading,
  uploadProgress,
  uploadedCount,
  onFilesAdded,
  onRemoveFile,
  onToggleType,
  onUpload,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)

  const rgbCount = files.filter((f) => f.type === 'rgb').length
  const thermalCount = files.filter((f) => f.type === 'thermal').length
  const gpsCount = 0 // would need EXIF reading client-side; placeholder
  const canUpload = rgbCount > 0 && thermalCount > 0

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragging(false)
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setDragging(false)
      const dropped = Array.from(e.dataTransfer.files)
      onFilesAdded(dropped)
    },
    [onFilesAdded]
  )

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (!e.target.files) return
      onFilesAdded(Array.from(e.target.files))
      e.target.value = '' // reset so same files can be re-added after remove
    },
    [onFilesAdded]
  )

  return (
    <div className="space-y-5">
      {/* Drop zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`relative min-h-64 rounded-2xl border-2 border-dashed flex flex-col items-center justify-center gap-3 cursor-pointer transition-all select-none ${
          dragging
            ? 'border-amber-400 bg-amber-500/10 scale-[1.01]'
            : 'border-gray-600 bg-[#2a2a2a] hover:border-amber-500/60 hover:bg-[#2f2f2f]'
        }`}
      >
        <div className="text-5xl">{dragging ? '📂' : '📸'}</div>
        <p className="text-white font-semibold text-lg">
          {dragging ? 'Relâchez pour ajouter' : 'Déposez vos images DJI ici'}
        </p>
        <p className="text-gray-400 text-sm text-center max-w-md px-4">
          Formats acceptés : .jpg .jpeg .tif .tiff .rjpeg — Plusieurs centaines d'images supportées
        </p>
        <button
          type="button"
          className="mt-1 px-5 py-2.5 bg-amber-500 text-black text-sm font-bold rounded-lg hover:bg-amber-400 transition-colors pointer-events-none"
        >
          Parcourir les fichiers
        </button>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".jpg,.jpeg,.tif,.tiff,.rjpeg"
          className="hidden"
          onChange={handleInputChange}
        />
      </div>

      {/* Counters */}
      {files.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { icon: '📷', label: 'RGB', value: rgbCount, color: 'text-blue-400' },
            { icon: '🌡️', label: 'Thermique', value: thermalCount, color: 'text-red-400' },
            { icon: '📍', label: 'Avec GPS', value: gpsCount, color: 'text-green-400' },
            {
              icon: '✅',
              label: 'Uploadées',
              value: `${uploadedCount}/${files.length}`,
              color: 'text-amber-400',
            },
          ].map(({ icon, label, value, color }) => (
            <div key={label} className="bg-[#2a2a2a] rounded-xl p-3 border border-gray-700">
              <p className="text-gray-500 text-xs mb-1">{icon} {label}</p>
              <p className={`text-2xl font-bold ${color}`}>{value}</p>
            </div>
          ))}
        </div>
      )}

      {/* File grid */}
      {files.length > 0 && (
        <div>
          <p className="text-gray-400 text-sm mb-3">
            {files.length} fichier{files.length > 1 ? 's' : ''} sélectionné{files.length > 1 ? 's' : ''}
          </p>
          <div className="grid grid-cols-3 sm:grid-cols-5 md:grid-cols-7 lg:grid-cols-9 gap-2 max-h-80 overflow-y-auto pr-1">
            {files.map((fi) => (
              <div key={fi.id} className="relative group aspect-square rounded-lg overflow-hidden bg-gray-800 border border-gray-700">
                {/* Preview or icon */}
                {fi.previewUrl ? (
                  <img
                    src={fi.previewUrl}
                    alt={fi.file.name}
                    className="w-full h-full object-cover"
                    loading="lazy"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-2xl text-gray-500">
                    🗂️
                  </div>
                )}

                {/* Type badge */}
                <button
                  type="button"
                  title="Cliquer pour changer le type"
                  onClick={(e) => { e.stopPropagation(); onToggleType(fi.id) }}
                  className={`absolute top-0.5 left-0.5 px-1.5 py-0.5 rounded text-[10px] font-bold uppercase leading-tight cursor-pointer border transition-colors ${
                    fi.type === 'thermal'
                      ? 'bg-red-900/90 text-red-300 border-red-700 hover:bg-red-700'
                      : 'bg-blue-900/90 text-blue-300 border-blue-700 hover:bg-blue-700'
                  }`}
                >
                  {fi.type === 'thermal' ? 'THM' : 'RGB'}
                </button>

                {/* Upload status overlay */}
                {fi.uploaded && (
                  <div className="absolute inset-0 bg-green-900/60 flex items-center justify-center">
                    <span className="text-green-300 text-xl">✓</span>
                  </div>
                )}
                {fi.error && (
                  <div className="absolute inset-0 bg-red-900/60 flex items-center justify-center">
                    <span className="text-red-300 text-xl">✗</span>
                  </div>
                )}

                {/* Remove button */}
                <button
                  type="button"
                  onClick={(e) => { e.stopPropagation(); onRemoveFile(fi.id) }}
                  className="absolute top-0.5 right-0.5 w-5 h-5 rounded-full bg-black/70 text-white text-xs flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600"
                  title="Retirer"
                >
                  ✕
                </button>

                {/* Filename tooltip */}
                <div className="absolute bottom-0 left-0 right-0 bg-black/70 text-[9px] text-gray-300 px-1 py-0.5 truncate opacity-0 group-hover:opacity-100 transition-opacity">
                  {truncate(fi.file.name, 16)}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Upload progress */}
      {uploading && (
        <div className="bg-[#2a2a2a] rounded-xl p-4 border border-amber-500/30">
          <div className="flex justify-between items-center mb-2">
            <span className="text-amber-400 text-sm font-semibold animate-pulse">Upload en cours…</span>
            <span className="text-white text-sm font-mono">{uploadProgress}%</span>
          </div>
          <div className="w-full h-3 bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-amber-500 rounded-full transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
          <p className="text-gray-400 text-xs mt-2">
            {uploadedCount} fichier{uploadedCount > 1 ? 's' : ''} uploadé{uploadedCount > 1 ? 's' : ''} sur {files.length}
          </p>
        </div>
      )}

      {/* Validation message */}
      {files.length > 0 && !canUpload && (
        <div className="flex items-center gap-2 text-amber-400 bg-amber-900/20 border border-amber-700/40 rounded-lg px-4 py-2.5 text-sm">
          ⚠️ Vous devez avoir au moins 1 photo RGB et 1 photo thermique pour lancer l'analyse.
        </div>
      )}

      {/* Upload button */}
      <div className="flex justify-end pt-2">
        <button
          type="button"
          disabled={!canUpload || uploading || files.length === 0}
          onClick={onUpload}
          className={`px-6 py-3 rounded-xl font-bold text-sm transition-all ${
            canUpload && !uploading && files.length > 0
              ? 'bg-amber-500 text-black hover:bg-amber-400 cursor-pointer shadow-lg shadow-amber-900/40'
              : 'bg-gray-700 text-gray-500 cursor-not-allowed'
          }`}
        >
          {uploading ? '⏳ Upload en cours\u2026' : "🚀 Valider et lancer l'analyse"}
        </button>
      </div>
    </div>
  )
}

// ─── Step 3 — Confirmation ────────────────────────────────────────────────────

interface Step3Props {
  inspectionId: string
  rgbCount: number
  thermalCount: number
}

const Step3: React.FC<Step3Props> = ({ inspectionId, rgbCount, thermalCount }) => {
  const navigate = useNavigate()
  return (
    <div className="flex flex-col items-center text-center py-8 gap-5">
      <div className="w-24 h-24 rounded-full bg-green-900/40 border-2 border-green-500 flex items-center justify-center text-5xl">
        ✅
      </div>
      <div>
        <h2 className="text-2xl font-bold text-white mb-2">Upload terminé !</h2>
        <p className="text-gray-300 text-lg font-semibold">
          {rgbCount} photos RGB + {thermalCount} photos thermiques uploadées
        </p>
      </div>
      <div className="bg-[#2a2a2a] rounded-xl border border-green-700/40 px-6 py-4 max-w-md text-sm text-gray-300">
        L'analyse IA démarre automatiquement. Vous serez notifié quand le rapport est prêt.
      </div>
      <div className="flex gap-3 mt-2 flex-wrap justify-center">
        <button
          type="button"
          onClick={() => navigate(`/inspections/${inspectionId}`)}
          className="px-5 py-2.5 bg-amber-500 text-black font-bold rounded-xl hover:bg-amber-400 transition-colors"
        >
          📊 Voir la progression
        </button>
        <button
          type="button"
          onClick={() => navigate('/inspections/new')}
          className="px-5 py-2.5 bg-[#2a2a2a] border border-gray-600 text-white font-semibold rounded-xl hover:border-gray-400 hover:bg-[#333] transition-colors"
        >
          ➕ Nouvelle inspection
        </button>
      </div>
    </div>
  )
}

// ─── Main page ────────────────────────────────────────────────────────────────

export const UploadPhotosPage: React.FC = () => {
  const navigate = useNavigate()
  const { inspectionId: paramId } = useParams<{ inspectionId?: string }>()

  const [step, setStep] = useState<Step>(1)
  const [selectedInspectionId, setSelectedInspectionId] = useState<string | null>(paramId ?? null)
  const [files, setFiles] = useState<FileItem[]>([])
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadedCount, setUploadedCount] = useState(0)

  // When preselected via URL param, jump straight to step 2 once we confirm payment
  const handleInspectionSelect = useCallback((id: string) => {
    setSelectedInspectionId(id)
    setStep(2)
  }, [])

  const handleFilesAdded = useCallback((newFiles: File[]) => {
    setFiles((prev) => {
      const existing = new Set(prev.map((f) => f.file.name + f.file.size))
      const toAdd: FileItem[] = []

      for (const file of newFiles) {
        const key = file.name + file.size
        if (existing.has(key)) continue
        existing.add(key)

        const type = detectType(file.name)
        // Use createObjectURL for performance — revoked on cleanup
        const previewUrl = isImageFile(file) ? URL.createObjectURL(file) : undefined

        toAdd.push({
          id: `${file.name}-${file.size}-${Math.random().toString(36).slice(2)}`,
          file,
          type,
          previewUrl,
          uploaded: false,
        })
      }
      return [...prev, ...toAdd]
    })
  }, [])

  const handleRemoveFile = useCallback((id: string) => {
    setFiles((prev) => {
      const item = prev.find((f) => f.id === id)
      if (item?.previewUrl) URL.revokeObjectURL(item.previewUrl)
      return prev.filter((f) => f.id !== id)
    })
  }, [])

  const handleToggleType = useCallback((id: string) => {
    setFiles((prev) =>
      prev.map((f) =>
        f.id === id ? { ...f, type: f.type === 'rgb' ? 'thermal' : 'rgb' } : f
      )
    )
  }, [])

  // Cleanup object URLs on unmount
  useEffect(() => {
    return () => {
      files.forEach((f) => {
        if (f.previewUrl) URL.revokeObjectURL(f.previewUrl)
      })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleUpload = useCallback(async () => {
    if (!selectedInspectionId) return

    const rgbFiles = files.filter((f) => f.type === 'rgb').map((f) => f.file)
    const thermalFiles = files.filter((f) => f.type === 'thermal').map((f) => f.file)

    if (rgbFiles.length === 0 || thermalFiles.length === 0) return

    setUploading(true)
    setUploadProgress(0)
    setUploadedCount(0)

    try {
      // Upload all files in a single multipart request
      const allFiles = files.map((f) => f.file)
      await inspectionsApi.uploadImages(selectedInspectionId, allFiles, (pct) => {
        setUploadProgress(pct)
        setUploadedCount(Math.round((pct / 100) * allFiles.length))
      })

      // Mark all as uploaded
      setFiles((prev) => prev.map((f) => ({ ...f, uploaded: true })))
      setUploadedCount(allFiles.length)
      setUploadProgress(100)

      // Start analysis
      try {
        await inspectionsApi.startAnalysis(selectedInspectionId)
      } catch {
        // Non-fatal: analysis might start via other means
      }

      setStep(3)
    } catch (err) {
      console.error('Upload error:', err)
      setFiles((prev) =>
        prev.map((f) => ({ ...f, error: f.uploaded ? undefined : 'Échec upload' }))
      )
    } finally {
      setUploading(false)
    }
  }, [selectedInspectionId, files])

  const rgbCount = files.filter((f) => f.type === 'rgb').length
  const thermalCount = files.filter((f) => f.type === 'thermal').length

  return (
    <div className="min-h-full bg-[#1a1a1a] p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-white">Télécharger des photos</h1>
          <p className="text-gray-400 mt-1 text-sm">
            Upload massif d'images drone RGB et thermiques pour votre inspection.
          </p>
        </div>

        {/* Step indicator */}
        <StepIndicator current={step} />

        {/* Card */}
        <div className="bg-[#2a2a2a] rounded-2xl border border-gray-700 p-6 shadow-xl">
          {step === 1 && (
            <Step1
              preselectedId={selectedInspectionId}
              onSelect={handleInspectionSelect}
            />
          )}

          {step === 2 && selectedInspectionId && (
            <>
              {/* Back + inspection info bar */}
              <div className="flex items-center justify-between mb-5">
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="text-gray-400 hover:text-white text-sm flex items-center gap-1 transition-colors"
                >
                  ← Changer d'inspection
                </button>
                <span className="text-xs text-amber-400 font-mono bg-amber-900/20 px-3 py-1 rounded-full border border-amber-700/40">
                  Inspection {selectedInspectionId.slice(0, 8)}…
                </span>
              </div>

              <Step2
                files={files}
                uploading={uploading}
                uploadProgress={uploadProgress}
                uploadedCount={uploadedCount}
                onFilesAdded={handleFilesAdded}
                onRemoveFile={handleRemoveFile}
                onToggleType={handleToggleType}
                onUpload={handleUpload}
              />
            </>
          )}

          {step === 3 && selectedInspectionId && (
            <Step3
              inspectionId={selectedInspectionId}
              rgbCount={rgbCount}
              thermalCount={thermalCount}
            />
          )}
        </div>

        {/* Bottom action for step 1 */}
        {step === 1 && (
          <div className="mt-4 text-center">
            <button
              type="button"
              onClick={() => navigate('/inspections/new')}
              className="text-amber-400 hover:text-amber-300 text-sm underline underline-offset-2 transition-colors"
            >
              Créer une nouvelle inspection →
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
