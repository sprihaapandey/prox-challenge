import { useMemo, useState } from 'react'
import type { DutyCycleRecord } from '../../types'
import { ArtifactCard, SourceFooter } from './ArtifactCard'

function formatMinutes(mins: number): string {
  if (Number.isInteger(mins)) return `${mins}`
  return mins.toFixed(1).replace(/\.0$/, '')
}

function DutyCycleWheel({ percent }: { percent: number }) {
  const r = 30
  const circumference = 2 * Math.PI * r
  const weldLength = (percent / 100) * circumference
  return (
    <svg width="76" height="76" viewBox="0 0 76 76" className="shrink-0 -rotate-90">
      <circle cx="38" cy="38" r={r} fill="none" stroke="var(--color-obsidian-elevated-2)" strokeWidth="8" />
      <circle
        cx="38"
        cy="38"
        r={r}
        fill="none"
        stroke="var(--color-ember)"
        strokeWidth="8"
        strokeLinecap="round"
        strokeDasharray={`${weldLength} ${circumference - weldLength}`}
        style={{ filter: 'drop-shadow(0 0 4px var(--color-ember-glow))' }}
      />
    </svg>
  )
}

export function DutyCycleCalculator({
  records,
  highlight,
}: {
  records: DutyCycleRecord[]
  highlight: { process: string; input_voltage: number; amperage: number } | null
}) {
  const processes = useMemo(() => [...new Set(records.map((r) => r.process))], [records])
  const [process, setProcess] = useState(highlight?.process ?? processes[0])
  const [voltage, setVoltage] = useState<number>(highlight?.input_voltage ?? 240)
  const [amperage, setAmperage] = useState<string>(highlight ? String(highlight.amperage) : '')

  const inRange = useMemo(() => records.filter((r) => r.process === process && r.input_voltage === voltage), [records, process, voltage])

  const amperageNum = amperage.trim() === '' ? null : Number(amperage)
  const match = amperageNum !== null ? inRange.find((r) => r.amperage === amperageNum) : null
  const showNotFound = amperageNum !== null && !match

  const selectClass =
    'rounded-lg border border-obsidian-border bg-obsidian-elevated px-2.5 py-1.5 text-sm font-medium text-ink outline-none transition focus:border-ember/50'

  return (
    <ArtifactCard title="Duty Cycle Calculator" icon="⏱️">
      <div className="flex flex-wrap gap-2">
        <select value={process} onChange={(e) => setProcess(e.target.value)} className={selectClass}>
          {processes.map((p) => (
            <option key={p} value={p}>
              {p}
            </option>
          ))}
        </select>
        <select value={voltage} onChange={(e) => setVoltage(Number(e.target.value))} className={selectClass}>
          <option value={120}>120V</option>
          <option value={240}>240V</option>
        </select>
        <div className="flex items-center gap-1.5 rounded-lg border border-obsidian-border bg-obsidian-elevated px-2.5 py-1.5">
          <input
            type="number"
            value={amperage}
            onChange={(e) => setAmperage(e.target.value)}
            placeholder="Amperage"
            className="w-20 bg-transparent text-sm font-medium text-ink outline-none placeholder:text-ink-faint"
          />
          <span className="text-xs text-ink-faint">A</span>
        </div>
      </div>

      {match && (
        <div className="mt-3 flex items-center gap-4 rounded-xl border border-ember/25 bg-ember-soft p-4">
          <DutyCycleWheel percent={match.duty_cycle_percent} />
          <div className="flex-1">
            <div className="text-3xl font-bold text-ember">{match.duty_cycle_percent}%</div>
            <div className="text-sm text-ink-muted">duty cycle at {match.amperage}A</div>
            <div className="mt-2 flex gap-4 text-sm">
              <div>
                <span className="font-semibold text-ink">{formatMinutes((match.duty_cycle_percent / 100) * 10)} min</span>{' '}
                <span className="text-ink-faint">welding</span>
              </div>
              <div>
                <span className="font-semibold text-ink">{formatMinutes(10 - (match.duty_cycle_percent / 100) * 10)} min</span>{' '}
                <span className="text-ink-faint">resting</span>
              </div>
            </div>
          </div>
        </div>
      )}
      {match && (
        <div className="text-xs text-ink-faint">
          Rated current range: {match.welding_current_range}
          <SourceFooter page={match.source_page} />
        </div>
      )}

      {showNotFound && (
        <div className="mt-3 rounded-xl border border-obsidian-border bg-obsidian-elevated/40 p-4 text-sm">
          <div className="font-medium text-ink-muted">
            The manual doesn't provide a duty-cycle value for {process} at exactly {amperageNum}A on {voltage}V.
          </div>
          {inRange.length > 0 && (
            <div className="mt-2">
              <div className="mb-1.5 text-xs text-ink-faint">Available data points for {process} at {voltage}V:</div>
              <div className="flex flex-wrap gap-1.5">
                {inRange.map((r) => (
                  <button
                    key={r.amperage}
                    onClick={() => setAmperage(String(r.amperage))}
                    className="rounded-full border border-obsidian-border-strong bg-obsidian-elevated px-2.5 py-1 text-xs font-medium text-ink-muted transition hover:border-ember/40 hover:text-ember"
                  >
                    {r.amperage}A → {r.duty_cycle_percent}%
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {amperageNum === null && <div className="mt-3 text-xs text-ink-faint">Enter an amperage, or pick one of the data points below.</div>}

      {amperageNum === null && inRange.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1.5">
          {inRange.map((r) => (
            <button
              key={r.amperage}
              onClick={() => setAmperage(String(r.amperage))}
              className="rounded-full border border-obsidian-border bg-obsidian-elevated px-2.5 py-1 text-xs font-medium text-ink-muted transition hover:border-ember/40 hover:text-ember"
            >
              {r.amperage}A → {r.duty_cycle_percent}%
            </button>
          ))}
        </div>
      )}
    </ArtifactCard>
  )
}
