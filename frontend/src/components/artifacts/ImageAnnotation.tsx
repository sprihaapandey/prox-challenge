import { useState } from 'react'
import type { ImageAnnotationPoint } from '../../types'
import { ArtifactCard } from './ArtifactCard'

const STATUS_COLOR: Record<ImageAnnotationPoint['status'], string> = {
  ok: 'var(--color-mint)',
  warning: 'var(--color-amber)',
  info: 'var(--color-ember)',
}

function clampPct(v: number): number {
  return Math.min(100, Math.max(0, v))
}

export function ImageAnnotation({ imageUrl, points }: { imageUrl: string; points: ImageAnnotationPoint[] }) {
  const [active, setActive] = useState<number | null>(null)

  return (
    <ArtifactCard title="Annotated Photo" icon="📍">
      <div className="relative overflow-hidden rounded-xl border border-obsidian-border bg-obsidian-elevated">
        <img src={imageUrl} alt="Uploaded photo with annotations" className="block w-full" />
        {points.map((p, i) => {
          const color = STATUS_COLOR[p.status]
          const isActive = active === i
          return (
            <button
              key={i}
              onClick={() => setActive(isActive ? null : i)}
              className="absolute flex h-6 w-6 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full text-[11px] font-bold text-white transition"
              style={{
                left: `${clampPct(p.x_pct)}%`,
                top: `${clampPct(p.y_pct)}%`,
                background: color,
                boxShadow: isActive ? `0 0 0 4px ${color}55, 0 0 16px ${color}` : `0 0 8px ${color}aa`,
                zIndex: isActive ? 10 : 1,
                transform: `translate(-50%, -50%) scale(${isActive ? 1.15 : 1})`,
              }}
              aria-label={p.label}
            >
              {i + 1}
            </button>
          )
        })}
      </div>

      <div className="mt-3 flex flex-col gap-1.5">
        {points.map((p, i) => {
          const color = STATUS_COLOR[p.status]
          const isActive = active === i
          return (
            <button
              key={i}
              onClick={() => setActive(isActive ? null : i)}
              className={`flex items-start gap-2.5 rounded-lg border px-3 py-2 text-left transition ${
                isActive ? 'border-obsidian-border-strong bg-obsidian-elevated' : 'border-transparent hover:bg-obsidian-elevated/50'
              }`}
            >
              <span
                className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-[10px] font-bold text-white"
                style={{ background: color }}
              >
                {i + 1}
              </span>
              <div className="text-sm">
                <div className="font-medium text-ink">{p.label}</div>
                <div className="text-ink-faint">{p.note}</div>
              </div>
            </button>
          )
        })}
      </div>
    </ArtifactCard>
  )
}
