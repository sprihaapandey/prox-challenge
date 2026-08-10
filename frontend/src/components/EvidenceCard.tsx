import type { EvidenceItem } from '../types'
import { useManualViewer } from '../context/ManualViewerContext'

function FactCard({ item }: { item: Extract<EvidenceItem, { type: 'fact' }> }) {
  const { openPage } = useManualViewer()
  const { fact_kind, data, page, doc_id } = item

  const wrap = (children: React.ReactNode) => (
    <button
      onClick={() => page && openPage(doc_id, page)}
      className="w-full rounded-lg border border-ember/25 bg-ember-soft px-3 py-2 text-left text-sm transition hover:border-ember/50 active:scale-[0.98]"
    >
      {children}
    </button>
  )

  if (fact_kind === 'duty_cycle' && data.found) {
    return wrap(
      <>
        <div className="font-semibold text-ink">
          {data.process} · {data.input_voltage}V · {data.amperage}A
        </div>
        <div className="text-ember">{data.duty_cycle_percent}% duty cycle</div>
        <div className="mt-0.5 text-xs text-ink-muted">Range: {data.welding_current_range} · Page {page}</div>
      </>,
    )
  }

  if (fact_kind === 'polarity' && data.found) {
    return wrap(
      <>
        <div className="font-semibold text-ink">
          {data.process} · {data.polarity_name || data.polarity_full_name}
        </div>
        <div className="text-ink-muted">
          {data.gun_or_torch_or_electrode_cable} → {data.gun_or_torch_or_electrode_socket} socket
        </div>
        <div className="text-ink-muted">Ground clamp → {data.ground_clamp_socket} socket</div>
        <div className="mt-0.5 text-xs text-ink-faint">Page {page}</div>
      </>,
    )
  }

  if (fact_kind === 'part' && data) {
    return wrap(
      <>
        <div className="font-semibold text-ink">Part #{data.part_number}</div>
        <div className="text-ink-muted">
          {data.description} (qty {data.qty})
        </div>
        <div className="mt-0.5 text-xs text-ink-faint">Page {page}</div>
      </>,
    )
  }

  return null
}

export function EvidenceCard({ item }: { item: EvidenceItem }) {
  const { openPage } = useManualViewer()

  if (item.type === 'visual' || item.type === 'page_image') {
    const title = item.type === 'visual' ? item.title : `Page ${item.page}`
    const caption = item.type === 'visual' ? item.description : item.section
    const bbox = item.type === 'visual' ? item.highlight_bbox_pct : null
    return (
      <button
        onClick={() => openPage(item.doc_id, item.page, bbox)}
        className="group block w-56 shrink-0 overflow-hidden rounded-xl border border-obsidian-border bg-obsidian-panel text-left transition hover:-translate-y-0.5 hover:border-obsidian-border-strong hover:shadow-[0_4px_20px_rgba(0,0,0,0.4),0_0_0_1px_var(--color-ember-glow)] active:translate-y-0 active:scale-[0.98]"
      >
        <div className="overflow-hidden bg-obsidian-elevated">
          <img
            src={item.image_url}
            alt={title}
            className="h-32 w-full object-cover object-top transition duration-300 group-hover:scale-105"
          />
        </div>
        <div className="px-2.5 py-2">
          <div className="truncate text-xs font-semibold text-ink">{title}</div>
          {caption && <div className="line-clamp-2 text-[11px] text-ink-faint">{caption}</div>}
          <div className="mt-1 text-[11px] font-medium text-ember">Manual — Page {item.page}</div>
        </div>
      </button>
    )
  }

  if (item.type === 'fact') {
    return <FactCard item={item} />
  }

  if (item.type === 'page_reference') {
    return (
      <button
        onClick={() => openPage(item.doc_id, item.page)}
        className="w-56 shrink-0 rounded-xl border border-obsidian-border bg-obsidian-panel px-2.5 py-2 text-left text-xs transition hover:-translate-y-0.5 hover:border-obsidian-border-strong active:translate-y-0 active:scale-[0.98]"
      >
        <div className="font-semibold text-ink-muted">
          Page {item.page}
          {item.section ? ` · ${item.section}` : ''}
        </div>
        <div className="line-clamp-3 text-ink-faint">{item.snippet}</div>
      </button>
    )
  }

  return null
}
