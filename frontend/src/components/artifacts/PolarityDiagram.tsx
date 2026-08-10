import { useState } from 'react'
import type { PolarityRecord } from '../../types'
import { ArtifactCard, SourceFooter } from './ArtifactCard'

function SocketBadge({ socket }: { socket: 'Positive' | 'Negative' }) {
  const isPositive = socket === 'Positive'
  return (
    <span
      className={`inline-flex h-7 w-7 items-center justify-center rounded-full text-sm font-bold ${
        isPositive ? 'bg-orange-500 text-white' : 'bg-neutral-800 text-white'
      }`}
    >
      {isPositive ? '+' : '−'}
    </span>
  )
}

function ConnectionRow({ label, cable, socket }: { label: string; cable: string; socket: 'Positive' | 'Negative' }) {
  return (
    <div className="flex items-center gap-3 rounded-xl border border-neutral-200 bg-neutral-50 px-3.5 py-3">
      <div className="flex-1">
        <div className="text-[11px] font-medium uppercase tracking-wide text-neutral-400">{label}</div>
        <div className="text-sm font-medium text-neutral-800">{cable}</div>
      </div>
      <div className="text-neutral-300">→</div>
      <div className="flex items-center gap-1.5">
        <SocketBadge socket={socket} />
        <span className="text-sm font-medium text-neutral-600">{socket}</span>
      </div>
    </div>
  )
}

export function PolarityDiagram({ records, highlight }: { records: PolarityRecord[]; highlight: string | null }) {
  const [selected, setSelected] = useState(highlight ?? records[0]?.process)
  const record = records.find((r) => r.process === selected) ?? records[0]
  if (!record) return null

  const isElectrode = record.gun_or_torch_or_electrode_cable.toLowerCase().includes('electrode')
  const gunLabel = isElectrode ? 'Electrode Holder' : record.gun_or_torch_or_electrode_cable.includes('Torch') ? 'Torch' : 'Gun / Wire Feed'

  return (
    <ArtifactCard title="Polarity & Cable Connections" icon="🔌">
      <div className="mb-3 flex gap-1.5">
        {records.map((r) => (
          <button
            key={r.process}
            onClick={() => setSelected(r.process)}
            className={`rounded-full px-3 py-1 text-xs font-medium transition ${
              r.process === selected ? 'bg-neutral-900 text-white' : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'
            }`}
          >
            {r.process}
          </button>
        ))}
      </div>

      <div className="mb-3 flex items-center gap-2">
        <span className="rounded-full bg-orange-100 px-2.5 py-1 text-xs font-semibold text-orange-800">
          {record.polarity_name || record.polarity_full_name}
        </span>
        <span className="text-xs text-neutral-500">{record.applies_to}</span>
      </div>

      <div className="flex flex-col gap-2">
        <ConnectionRow label={gunLabel} cable={record.gun_or_torch_or_electrode_cable} socket={record.gun_or_torch_or_electrode_socket} />
        <ConnectionRow label="Ground Clamp" cable="Ground Clamp Cable" socket={record.ground_clamp_socket} />
      </div>

      <SourceFooter page={record.source_page} />
    </ArtifactCard>
  )
}
