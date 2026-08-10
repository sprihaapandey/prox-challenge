import type { EvidenceItem } from '../types'
import { useManualViewer } from '../context/ManualViewerContext'

function FactCard({ item }: { item: Extract<EvidenceItem, { type: 'fact' }> }) {
  const { openPage } = useManualViewer()
  const { fact_kind, data, page, doc_id } = item

  const wrap = (children: React.ReactNode) => (
    <button
      onClick={() => page && openPage(doc_id, page)}
      className="w-full rounded-lg border border-orange-200 bg-orange-50 px-3 py-2 text-left text-sm transition hover:border-orange-300"
    >
      {children}
    </button>
  )

  if (fact_kind === 'duty_cycle' && data.found) {
    return wrap(
      <>
        <div className="font-semibold text-orange-900">
          {data.process} · {data.input_voltage}V · {data.amperage}A
        </div>
        <div className="text-orange-800">{data.duty_cycle_percent}% duty cycle</div>
        <div className="mt-0.5 text-xs text-orange-700">Range: {data.welding_current_range} · Page {page}</div>
      </>,
    )
  }

  if (fact_kind === 'polarity' && data.found) {
    return wrap(
      <>
        <div className="font-semibold text-orange-900">
          {data.process} · {data.polarity_name || data.polarity_full_name}
        </div>
        <div className="text-orange-800">
          {data.gun_or_torch_or_electrode_cable} → {data.gun_or_torch_or_electrode_socket} socket
        </div>
        <div className="text-orange-800">Ground clamp → {data.ground_clamp_socket} socket</div>
        <div className="mt-0.5 text-xs text-orange-700">Page {page}</div>
      </>,
    )
  }

  if (fact_kind === 'part' && data) {
    return wrap(
      <>
        <div className="font-semibold text-orange-900">Part #{data.part_number}</div>
        <div className="text-orange-800">
          {data.description} (qty {data.qty})
        </div>
        <div className="mt-0.5 text-xs text-orange-700">Page {page}</div>
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
        className="block w-56 shrink-0 overflow-hidden rounded-lg border border-neutral-200 bg-white text-left shadow-sm transition hover:shadow-md"
      >
        <img src={item.image_url} alt={title} className="h-32 w-full object-cover object-top bg-neutral-50" />
        <div className="px-2.5 py-2">
          <div className="truncate text-xs font-semibold text-neutral-800">{title}</div>
          {caption && <div className="line-clamp-2 text-[11px] text-neutral-500">{caption}</div>}
          <div className="mt-1 text-[11px] font-medium text-orange-600">Manual — Page {item.page}</div>
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
        className="w-56 shrink-0 rounded-lg border border-neutral-200 bg-white px-2.5 py-2 text-left text-xs shadow-sm transition hover:shadow-md"
      >
        <div className="font-semibold text-neutral-700">
          Page {item.page}
          {item.section ? ` · ${item.section}` : ''}
        </div>
        <div className="line-clamp-3 text-neutral-500">{item.snippet}</div>
      </button>
    )
  }

  return null
}
