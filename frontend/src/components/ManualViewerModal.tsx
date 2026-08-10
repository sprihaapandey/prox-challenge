import { useEffect, useState } from 'react'
import { useManualViewer } from '../context/ManualViewerContext'
import { docPageCount, docTitle } from '../lib/docMeta'
import { pageImageUrl } from '../lib/media'

const MIN_ZOOM = 1
const MAX_ZOOM = 3
const ZOOM_STEP = 0.5

function validBbox(bbox: [number, number, number, number] | null | undefined): [number, number, number, number] | null {
  if (!bbox || bbox.length !== 4) return null
  const [x0, y0, x1, y1] = bbox
  const inRange = [x0, y0, x1, y1].every((v) => typeof v === 'number' && v >= 0 && v <= 100)
  const nonDegenerate = Math.abs(x1 - x0) >= 2 && Math.abs(y1 - y0) >= 2
  return inRange && nonDegenerate ? bbox : null
}

export function ManualViewerModal() {
  const { state, close, openPage } = useManualViewer()
  const [zoom, setZoom] = useState(1)
  const [pageInput, setPageInput] = useState('')

  useEffect(() => {
    setZoom(1)
    if (state) setPageInput(String(state.page))
  }, [state?.docId, state?.page])

  useEffect(() => {
    if (!state) return
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') close()
      else if (e.key === 'ArrowLeft') goToPage(state.page - 1)
      else if (e.key === 'ArrowRight') goToPage(state.page + 1)
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state])

  if (!state) return null

  const total = docPageCount(state.docId)

  const goToPage = (page: number) => {
    if (page < 1 || page > total) return
    openPage(state.docId, page)
  }

  const submitPageInput = () => {
    const n = Number(pageInput)
    if (Number.isInteger(n)) goToPage(n)
    else setPageInput(String(state.page))
  }

  const bbox = validBbox(state.highlightBboxPct)

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
      onClick={close}
      role="dialog"
      aria-modal="true"
    >
      <div
        className="flex max-h-full w-full max-w-4xl flex-col overflow-hidden rounded-2xl border border-obsidian-border-strong bg-obsidian-panel shadow-[0_20px_60px_rgba(0,0,0,0.6)]"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-obsidian-border px-4 py-2.5">
          <div className="text-sm font-semibold text-ink">{docTitle(state.docId)}</div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 text-xs text-ink-muted">
              <button
                onClick={() => setZoom((z) => Math.max(MIN_ZOOM, z - ZOOM_STEP))}
                disabled={zoom <= MIN_ZOOM}
                className="flex h-6 w-6 items-center justify-center rounded border border-obsidian-border text-ink-muted transition hover:border-obsidian-border-strong hover:text-ink disabled:opacity-30"
                aria-label="Zoom out"
              >
                −
              </button>
              <span className="w-9 text-center">{Math.round(zoom * 100)}%</span>
              <button
                onClick={() => setZoom((z) => Math.min(MAX_ZOOM, z + ZOOM_STEP))}
                disabled={zoom >= MAX_ZOOM}
                className="flex h-6 w-6 items-center justify-center rounded border border-obsidian-border text-ink-muted transition hover:border-obsidian-border-strong hover:text-ink disabled:opacity-30"
                aria-label="Zoom in"
              >
                +
              </button>
            </div>
            <button onClick={close} className="text-ink-faint transition hover:text-ink" aria-label="Close">
              ✕
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-auto bg-obsidian p-6">
          <div className="relative mx-auto w-fit" style={{ width: `${zoom * 100}%`, maxWidth: zoom === 1 ? '100%' : 'none' }}>
            <img
              src={pageImageUrl(state.page, state.docId)}
              alt={`Page ${state.page}`}
              className="w-full rounded-lg shadow-[0_10px_40px_rgba(0,0,0,0.5)]"
            />
            {bbox && (
              <div
                className="pointer-events-none absolute rounded-sm border-2 border-ember bg-ember/20"
                style={{
                  left: `${Math.min(bbox[0], bbox[2])}%`,
                  top: `${Math.min(bbox[1], bbox[3])}%`,
                  width: `${Math.abs(bbox[2] - bbox[0])}%`,
                  height: `${Math.abs(bbox[3] - bbox[1])}%`,
                  boxShadow: '0 0 20px var(--color-ember-glow)',
                }}
              />
            )}
          </div>
        </div>

        <div className="flex items-center justify-center gap-3 border-t border-obsidian-border px-4 py-2.5">
          <button
            onClick={() => goToPage(state.page - 1)}
            disabled={state.page <= 1}
            className="rounded-lg border border-obsidian-border px-2.5 py-1 text-sm text-ink-muted transition hover:border-obsidian-border-strong hover:text-ink disabled:opacity-30"
          >
            ← Prev
          </button>
          <div className="flex items-center gap-1.5 text-sm text-ink-muted">
            <input
              value={pageInput}
              onChange={(e) => setPageInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && submitPageInput()}
              onBlur={submitPageInput}
              className="w-10 rounded border border-obsidian-border bg-obsidian-elevated px-1.5 py-0.5 text-center text-ink outline-none focus:border-ember/50"
            />
            <span className="text-ink-faint">of {total}</span>
          </div>
          <button
            onClick={() => goToPage(state.page + 1)}
            disabled={state.page >= total}
            className="rounded-lg border border-obsidian-border px-2.5 py-1 text-sm text-ink-muted transition hover:border-obsidian-border-strong hover:text-ink disabled:opacity-30"
          >
            Next →
          </button>
        </div>
      </div>
    </div>
  )
}
