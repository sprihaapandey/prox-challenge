import { useState } from 'react'
import type { TroubleshootingTableMatch, WeldDiagnosisMatch } from '../../types'
import { ArtifactCard, SourceFooter } from './ArtifactCard'

function CauseChecklist({ causes, actions }: { causes: string[]; actions: string[] }) {
  const [checked, setChecked] = useState<Set<number>>(new Set())

  const toggle = (i: number) => {
    setChecked((prev) => {
      const next = new Set(prev)
      if (next.has(i)) next.delete(i)
      else next.add(i)
      return next
    })
  }

  return (
    <div className="flex flex-col gap-2">
      {causes.map((cause, i) => {
        const isChecked = checked.has(i)
        return (
          <button
            key={i}
            onClick={() => toggle(i)}
            className={`flex items-start gap-2.5 rounded-lg border px-3 py-2.5 text-left transition ${
              isChecked ? 'border-green-200 bg-green-50' : 'border-neutral-200 bg-neutral-50 hover:border-orange-200'
            }`}
          >
            <span
              className={`mt-0.5 flex h-4.5 w-4.5 shrink-0 items-center justify-center rounded-full border text-[10px] ${
                isChecked ? 'border-green-500 bg-green-500 text-white' : 'border-neutral-300 text-transparent'
              }`}
            >
              ✓
            </span>
            <div className="text-sm">
              <div className={`font-medium ${isChecked ? 'text-green-800 line-through' : 'text-neutral-800'}`}>{cause}</div>
              <div className="mt-0.5 text-neutral-500">{actions[i]}</div>
            </div>
          </button>
        )
      })}
    </div>
  )
}

function TableMatchBlock({ match }: { match: TroubleshootingTableMatch }) {
  return (
    <div>
      <div className="mb-2 text-sm font-semibold text-neutral-800">{match.symptom}</div>
      <CauseChecklist causes={match.possible_causes} actions={match.recommended_actions} />
      <SourceFooter page={match.source_pages[0]} />
    </div>
  )
}

function DiagnosisMatchBlock({ match }: { match: WeldDiagnosisMatch }) {
  return (
    <div>
      <div className="mb-0.5 text-sm font-semibold text-neutral-800">{match.defect_name}</div>
      <div className="mb-2 text-xs text-neutral-500">{match.visual_description}</div>
      <CauseChecklist
        causes={match.possible_causes_and_solutions.map((c) => c.cause)}
        actions={match.possible_causes_and_solutions.map((c) => c.solution)}
      />
      <SourceFooter page={match.source_page} />
    </div>
  )
}

export function TroubleshootingFlowchart({
  matchType,
  tableMatches,
  diagnosisMatches,
}: {
  matchType: 'exact' | 'semantic'
  tableMatches: TroubleshootingTableMatch[]
  diagnosisMatches: WeldDiagnosisMatch[]
}) {
  if (tableMatches.length === 0 && diagnosisMatches.length === 0) return null

  return (
    <ArtifactCard title="Troubleshooting Guide" icon="🛠️">
      {matchType === 'semantic' && (
        <div className="mb-3 rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-800">
          No exact symptom match — showing the closest matches by meaning. Click a cause to mark it checked.
        </div>
      )}
      <div className="flex flex-col gap-5">
        {tableMatches.map((m, i) => (
          <TableMatchBlock key={`t${i}`} match={m} />
        ))}
        {diagnosisMatches.map((m, i) => (
          <DiagnosisMatchBlock key={`d${i}`} match={m} />
        ))}
      </div>
    </ArtifactCard>
  )
}
