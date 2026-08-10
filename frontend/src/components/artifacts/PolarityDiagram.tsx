import { useState } from 'react'
import type { PolarityRecord } from '../../types'
import { ArtifactCard, SourceFooter } from './ArtifactCard'

function SocketBadge({ socket }: { socket: 'Positive' | 'Negative' }) {
  const isPositive = socket === 'Positive'
  return (
    <span
      className={`inline-flex h-7 w-7 items-center justify-center rounded-full text-sm font-bold ${
        isPositive
          ? 'bg-gradient-to-br from-ember to-ember-dim text-white shadow-[0_0_10px_var(--color-ember-glow)]'
          : 'bg-obsidian-elevated-2 text-ink'
      }`}
    >
      {isPositive ? '+' : '−'}
    </span>
  )
}

function ConnectionRow({ label, cable, socket }: { label: string; cable: string; socket: 'Positive' | 'Negative' }) {
  return (
    <div className="flex items-center gap-3 rounded-xl border border-obsidian-border bg-obsidian-elevated/40 px-3.5 py-3">
      <div className="flex-1">
        <div className="text-[11px] font-medium uppercase tracking-wide text-ink-faint">{label}</div>
        <div className="text-sm font-medium text-ink">{cable}</div>
      </div>
      <div className="text-ink-faint">→</div>
      <div className="flex items-center gap-1.5">
        <SocketBadge socket={socket} />
        <span className="text-sm font-medium text-ink-muted">{socket}</span>
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
              r.process === selected ? 'bg-ink text-obsidian' : 'bg-obsidian-elevated text-ink-muted hover:bg-obsidian-elevated-2 hover:text-ink'
            }`}
          >
            {r.process}
          </button>
        ))}
      </div>

      <div className="mb-3 flex items-center gap-2">
        <span className="rounded-full border border-ember/30 bg-ember-soft px-2.5 py-1 text-xs font-semibold text-ember">
          {record.polarity_name || record.polarity_full_name}
        </span>
        <span className="text-xs text-ink-faint">{record.applies_to}</span>
      </div>

      <div className="flex flex-col gap-2">
        <ConnectionRow label={gunLabel} cable={record.gun_or_torch_or_electrode_cable} socket={record.gun_or_torch_or_electrode_socket} />
        <ConnectionRow label="Ground Clamp" cable="Ground Clamp Cable" socket={record.ground_clamp_socket} />
      </div>

      <SourceFooter page={record.source_page} />
    </ArtifactCard>
  )
}
