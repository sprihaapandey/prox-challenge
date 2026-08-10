import { useMemo, useState } from 'react'
import type { DutyCycleRecord } from '../../types'
import { ArtifactCard, SourceFooter } from './ArtifactCard'

function formatMinutes(mins: number): string {
  if (Number.isInteger(mins)) return `${mins}`
  return mins.toFixed(1).replace(/\.0$/, '')
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

  return (
    <ArtifactCard title="Duty Cycle Calculator" icon="⏱️">
      <div className="flex flex-wrap gap-2">
        <select
          value={process}
          onChange={(e) => setProcess(e.target.value)}
          className="rounded-lg border border-neutral-200 px-2.5 py-1.5 text-sm font-medium text-neutral-700"
        >
          {processes.map((p) => (
            <option key={p} value={p}>
              {p}
            </option>
          ))}
        </select>
        <select
          value={voltage}
          onChange={(e) => setVoltage(Number(e.target.value))}
          className="rounded-lg border border-neutral-200 px-2.5 py-1.5 text-sm font-medium text-neutral-700"
        >
          <option value={120}>120V</option>
          <option value={240}>240V</option>
        </select>
        <div className="flex items-center gap-1.5 rounded-lg border border-neutral-200 px-2.5 py-1.5">
          <input
            type="number"
            value={amperage}
            onChange={(e) => setAmperage(e.target.value)}
            placeholder="Amperage"
            className="w-20 text-sm font-medium text-neutral-700 outline-none"
          />
          <span className="text-xs text-neutral-400">A</span>
        </div>
      </div>

      {match && (
        <div className="mt-3 rounded-xl border border-orange-200 bg-orange-50 p-4">
          <div className="text-3xl font-bold text-orange-700">{match.duty_cycle_percent}%</div>
          <div className="text-sm text-orange-800">duty cycle at {match.amperage}A</div>
          <div className="mt-2 flex gap-4 text-sm">
            <div>
              <span className="font-semibold text-neutral-800">{formatMinutes((match.duty_cycle_percent / 100) * 10)} min</span>{' '}
              <span className="text-neutral-500">welding</span>
            </div>
            <div>
              <span className="font-semibold text-neutral-800">{formatMinutes(10 - (match.duty_cycle_percent / 100) * 10)} min</span>{' '}
              <span className="text-neutral-500">resting</span>
            </div>
          </div>
          <div className="mt-2 text-xs text-neutral-500">Rated current range: {match.welding_current_range}</div>
          <SourceFooter page={match.source_page} />
        </div>
      )}

      {showNotFound && (
        <div className="mt-3 rounded-xl border border-neutral-200 bg-neutral-50 p-4 text-sm">
          <div className="font-medium text-neutral-700">
            The manual doesn't provide a duty-cycle value for {process} at exactly {amperageNum}A on {voltage}V.
          </div>
          {inRange.length > 0 && (
            <div className="mt-2">
              <div className="mb-1.5 text-xs text-neutral-500">Available data points for {process} at {voltage}V:</div>
              <div className="flex flex-wrap gap-1.5">
                {inRange.map((r) => (
                  <button
                    key={r.amperage}
                    onClick={() => setAmperage(String(r.amperage))}
                    className="rounded-full border border-neutral-300 bg-white px-2.5 py-1 text-xs font-medium text-neutral-600 hover:border-orange-300 hover:text-orange-700"
                  >
                    {r.amperage}A → {r.duty_cycle_percent}%
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {amperageNum === null && (
        <div className="mt-3 text-xs text-neutral-400">Enter an amperage, or pick one of the data points below.</div>
      )}

      {amperageNum === null && inRange.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1.5">
          {inRange.map((r) => (
            <button
              key={r.amperage}
              onClick={() => setAmperage(String(r.amperage))}
              className="rounded-full border border-neutral-200 bg-white px-2.5 py-1 text-xs font-medium text-neutral-600 hover:border-orange-300 hover:text-orange-700"
            >
              {r.amperage}A → {r.duty_cycle_percent}%
            </button>
          ))}
        </div>
      )}
    </ArtifactCard>
  )
}
