import { useRef, useState } from 'react'
import { uploadImage } from '../lib/api'
import { useSpeechRecognition } from '../hooks/useSpeechRecognition'

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
  const baseTextRef = useRef('')
  const { isSupported: voiceSupported, isListening, interimTranscript, start, stop } = useSpeechRecognition()

  const submit = () => {
    const trimmed = text.trim()
    if (!trimmed && images.length === 0) return
    if (isListening) stop()
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

  const toggleVoice = () => {
    if (isListening) {
      stop()
      return
    }
    baseTextRef.current = text ? text + ' ' : ''
    start((finalChunk) => {
      baseTextRef.current += finalChunk + ' '
      setText(baseTextRef.current)
    })
  }

  const displayedText = isListening ? baseTextRef.current + interimTranscript : text

  return (
    <div className="border-t border-obsidian-border bg-obsidian px-3 py-3 sm:px-4">
      {images.length > 0 && (
        <div className="mb-2 flex gap-2">
          {images.map((img, i) => (
            <div key={i} className="relative">
              <img src={img.url} alt="attachment" className="h-16 w-16 rounded-lg border border-obsidian-border object-cover" />
              <button
                onClick={() => setImages((prev) => prev.filter((_, idx) => idx !== i))}
                className="absolute -right-1.5 -top-1.5 flex h-5 w-5 items-center justify-center rounded-full bg-obsidian-elevated-2 text-xs text-ink"
                aria-label="Remove image"
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}
      {uploading && (
        <div className="mb-2 flex items-center gap-1.5 text-xs text-ink-faint">
          <span className="h-1 w-1 animate-pulse rounded-full bg-ember" />
          Uploading photo…
        </div>
      )}
      {isListening && (
        <div className="mb-2 flex items-center gap-1.5 text-xs text-ember">
          <span className="h-1 w-1 animate-pulse rounded-full bg-ember" />
          Listening…
        </div>
      )}
      <div className="flex items-end gap-2">
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled || uploading}
          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-obsidian-border text-ink-muted transition hover:border-obsidian-border-strong hover:text-ink active:scale-90 disabled:opacity-40 disabled:active:scale-100"
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
        {voiceSupported && (
          <button
            onClick={toggleVoice}
            disabled={disabled}
            className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full border transition active:scale-90 disabled:opacity-40 disabled:active:scale-100 ${
              isListening
                ? 'border-ember/50 bg-ember-soft text-ember shadow-[0_0_16px_var(--color-ember-glow)]'
                : 'border-obsidian-border text-ink-muted hover:border-obsidian-border-strong hover:text-ink'
            }`}
            title={isListening ? 'Stop listening' : 'Speak your question'}
            aria-label={isListening ? 'Stop listening' : 'Speak your question'}
          >
            {isListening ? '◼' : '🎙️'}
          </button>
        )}
        <textarea
          value={displayedText}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              submit()
            }
          }}
          placeholder="Ask about your welder..."
          rows={1}
          className="max-h-32 flex-1 resize-none rounded-2xl border border-obsidian-border bg-obsidian-panel px-4 py-2.5 text-[15px] text-ink placeholder:text-ink-faint outline-none transition focus:border-ember/50 focus:shadow-[0_0_0_3px_var(--color-ember-soft)]"
        />
        <button
          onClick={submit}
          disabled={disabled || (!text.trim() && !isListening && images.length === 0)}
          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-ember to-ember-dim text-white shadow-[0_0_16px_var(--color-ember-glow)] transition active:scale-90 disabled:opacity-30 disabled:shadow-none disabled:active:scale-100"
          aria-label="Send"
        >
          ↑
        </button>
      </div>
    </div>
  )
}
