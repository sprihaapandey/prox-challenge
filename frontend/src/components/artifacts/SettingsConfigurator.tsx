import { useState } from 'react'
import type { SettingsCapability } from '../../types'
import { ArtifactCard, SourceFooter } from './ArtifactCard'

function Chip({ children }: { children: string }) {
  return <span className="rounded-full bg-neutral-100 px-2.5 py-1 text-xs font-medium text-neutral-700">{children}</span>
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="py-1.5">
      <div className="mb-1 text-[11px] font-medium uppercase tracking-wide text-neutral-400">{label}</div>
      {children}
    </div>
  )
}

export function SettingsConfigurator({
  capabilities,
  importantCaveat,
  highlight,
}: {
  capabilities: SettingsCapability[]
  importantCaveat: string
  highlight: string | null
}) {
  const [selected, setSelected] = useState(highlight ?? capabilities[0]?.process)
  const cap = capabilities.find((c) => c.process === selected) ?? capabilities[0]
  if (!cap) return null

  return (
    <ArtifactCard title="Settings Configurator" icon="⚙️">
      <div className="mb-3 rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-800">{importantCaveat}</div>

      <div className="mb-3 flex gap-1.5">
        {capabilities.map((c) => (
          <button
            key={c.process}
            onClick={() => setSelected(c.process)}
            className={`rounded-full px-3 py-1 text-xs font-medium transition ${
              c.process === selected ? 'bg-neutral-900 text-white' : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'
            }`}
          >
            {c.process}
          </button>
        ))}
      </div>

      <div className="divide-y divide-neutral-100">
        {(cap.wire_diameters || cap.electrode_types_shown_on_lcd) && (
          <Row label={cap.wire_diameters ? 'Wire diameter options' : 'Electrode types (LCD)'}>
            <div className="flex flex-wrap gap-1.5">
              {(cap.wire_diameters ?? cap.electrode_types_shown_on_lcd ?? []).map((d) => (
                <Chip key={d}>{d}</Chip>
              ))}
            </div>
          </Row>
        )}
        {cap.rod_or_electrode && (
          <Row label="Rod / Electrode">
            <div className="text-sm text-neutral-700">{cap.rod_or_electrode}</div>
          </Row>
        )}
        <Row label="Shielding gas">
          <div className="text-sm text-neutral-700">
            {cap.gas}
            {cap.gas_flow_scfh_range && <span className="text-neutral-500"> · {cap.gas_flow_scfh_range} SCFH</span>}
          </div>
        </Row>
        {cap.polarity && (
          <Row label="Polarity">
            <Chip>{cap.polarity}</Chip>
          </Row>
        )}
        {cap.weldable_materials && (
          <Row label="Weldable materials">
            <div className="flex flex-wrap gap-1.5">
              {cap.weldable_materials.map((m) => (
                <Chip key={m}>{m}</Chip>
              ))}
            </div>
          </Row>
        )}
      </div>

      <SourceFooter page={cap.source_page} />
    </ArtifactCard>
  )
}
