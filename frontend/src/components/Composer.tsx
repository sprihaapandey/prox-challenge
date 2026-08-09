import { useRef, useState } from 'react'
import { uploadImage } from '../lib/api'

interface PendingImage {
  path: string
  url: string
}

interface Props {
  disabled: boolean
  onSend: (text: string, imagePaths?: string[], imageUrls?: string[]) => void
}

export function Composer({ disabled, onSend }: Props) {
  const [text, setText] = useState('')
  const [images, setImages] = useState<PendingImage[]>([])
  const [uploading, setUploading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const submit = () => {
    const trimmed = text.trim()
    if (!trimmed && images.length === 0) return
    onSend(trimmed || 'What do you see in this photo?', images.map((i) => i.path), images.map((i) => i.url))
    setText('')
    setImages([])
  }

  const onFilesSelected = async (files: FileList | null) => {
    if (!files || files.length === 0) return
    setUploading(true)
    try {
      const uploaded = await Promise.all(Array.from(files).map(uploadImage))
      setImages((prev) => [...prev, ...uploaded])
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="border-t border-neutral-200 bg-white px-4 py-3">
      {images.length > 0 && (
        <div className="mb-2 flex gap-2">
          {images.map((img, i) => (
            <div key={i} className="relative">
              <img src={img.url} alt="attachment" className="h-16 w-16 rounded-lg object-cover border border-neutral-200" />
              <button
                onClick={() => setImages((prev) => prev.filter((_, idx) => idx !== i))}
                className="absolute -right-1.5 -top-1.5 flex h-5 w-5 items-center justify-center rounded-full bg-neutral-800 text-xs text-white"
                aria-label="Remove image"
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}
      <div className="flex items-end gap-2">
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled || uploading}
          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-neutral-200 text-neutral-500 hover:bg-neutral-50 disabled:opacity-50"
          title="Attach a photo"
          aria-label="Attach a photo"
        >
          📷
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          multiple
          className="hidden"
          onChange={(e) => onFilesSelected(e.target.files)}
        />
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              submit()
            }
          }}
          placeholder="Ask about your welder..."
          rows={1}
          className="max-h-32 flex-1 resize-none rounded-2xl border border-neutral-200 px-4 py-2.5 text-[15px] outline-none focus:border-orange-400"
        />
        <button
          onClick={submit}
          disabled={disabled || (!text.trim() && images.length === 0)}
          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-orange-500 text-white disabled:opacity-40"
          aria-label="Send"
        >
          ↑
        </button>
      </div>
    </div>
  )
}
