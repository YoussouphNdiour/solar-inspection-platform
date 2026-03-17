import React, { useCallback, useRef, useState } from 'react'

interface FileDropZoneProps {
  onFileChange: (file: File | null) => void
  value?: File | null
}

const ACCEPTED_EXTENSIONS = ['.kml', '.kmz', '.pdf', '.dwg', '.cad', '.stl']
const MAX_SIZE_BYTES = 25 * 1024 * 1024 // 25 Mo

export const FileDropZone: React.FC<FileDropZoneProps> = ({ onFileChange, value }) => {
  const [isDragging, setIsDragging] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const validateFile = (file: File): string | null => {
    const ext = '.' + file.name.split('.').pop()?.toLowerCase()
    if (!ACCEPTED_EXTENSIONS.includes(ext)) {
      return `Format non supporté. Formats acceptés : ${ACCEPTED_EXTENSIONS.join(' ')}`
    }
    if (file.size > MAX_SIZE_BYTES) {
      return 'Fichier trop volumineux. Taille maximale : 25 Mo'
    }
    return null
  }

  const handleFile = useCallback(
    (file: File) => {
      const err = validateFile(file)
      if (err) {
        setError(err)
        onFileChange(null)
      } else {
        setError(null)
        onFileChange(file)
      }
    },
    [onFileChange]
  )

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const onDragLeave = () => {
    setIsDragging(false)
  }

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  const onInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
  }

  const onClick = () => {
    inputRef.current?.click()
  }

  const onRemove = (e: React.MouseEvent) => {
    e.stopPropagation()
    setError(null)
    onFileChange(null)
    if (inputRef.current) inputRef.current.value = ''
  }

  return (
    <div className="w-full">
      <div
        onClick={onClick}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        className={`
          cursor-pointer rounded-lg px-6 py-8 text-center
          bg-gray-800 border-2 border-dashed transition-colors
          ${isDragging ? 'border-amber-500 bg-gray-700' : 'border-gray-600 hover:border-amber-500'}
        `}
      >
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED_EXTENSIONS.join(',')}
          className="hidden"
          onChange={onInputChange}
        />

        {value ? (
          <div className="flex items-center justify-center gap-3">
            <span className="text-2xl">📄</span>
            <div className="text-left">
              <p className="text-white font-medium text-sm">{value.name}</p>
              <p className="text-gray-400 text-xs">{(value.size / 1024 / 1024).toFixed(2)} Mo</p>
            </div>
            <button
              type="button"
              onClick={onRemove}
              className="ml-4 text-red-400 hover:text-red-300 text-lg font-bold"
              title="Supprimer le fichier"
            >
              ×
            </button>
          </div>
        ) : (
          <>
            <div className="text-4xl mb-3">☁️</div>
            <p className="text-white text-sm font-medium">
              Déposez votre fichier ici ou cliquez pour parcourir
            </p>
            <p className="text-gray-400 text-xs mt-1">
              Formats : .kml .kmz .pdf .dwg .cad .stl — Max 25 Mo
            </p>
          </>
        )}
      </div>

      {error && (
        <p className="mt-2 text-red-400 text-xs">{error}</p>
      )}
    </div>
  )
}
