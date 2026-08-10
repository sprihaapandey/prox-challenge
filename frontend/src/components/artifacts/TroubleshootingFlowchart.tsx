import { useState } from 'react'
import type { TroubleshootingTableMatch, WeldDiagnosisMatch } from '../../types'
import { ArtifactCard, SourceFooter } from './ArtifactCard'

/** A genuine root -> branches tree: one symptom/defect node at top, a trunk
 * line running down, and each cause branching off it with its matching
 * action. Faithful to the manual's actual data shape (a flat list of
 * cause/action pairs per symptom) rather than inventing yes/no decision
 * branches that aren't in the source. */
function FlowTree({ root, causes, actions }: { root: string; causes: string[]; actions: string[] }) {
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
    <div>
      {/* Root node */}
      <div className="flex items-center gap-2.5 rounded-xl border border-ember/40 bg-ember-soft px-3.5 py-2.5 shadow-[0_0_20px_var(--color-ember-glow)]">
        <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-ember text-xs font-bold text-white">⚠</span>
        <span className="text-sm font-semibold text-ink">{root}</span>
      </div>

      {/* Trunk + branches */}
      <div className="relative pl-7">
        <div className="absolute left-[13px] top-0 h-3 w-px bg-obsidian-border-strong" />
        <div className="relative mt-3 flex flex-col gap-2.5">
          <div className="absolute left-[-14px] top-0 bottom-3 w-px bg-obsidian-border-strong" />
          {causes.map((cause, i) => {
            const isChecked = checked.has(i)
            return (
              <div key={i} className="relative">
                <span className="absolute -left-7 top-[15px] h-px w-3.5 bg-obsidian-border-strong" />
                <span
                  className={`absolute -left-[30px] top-[11px] h-2.5 w-2.5 rounded-full border-2 transition ${
                    isChecked ? 'border-mint bg-mint' : 'border-ember bg-obsidian'
                  }`}
                />
                <button
                  onClick={() => toggle(i)}
                  className={`w-full rounded-lg border px-3 py-2.5 text-left transition ${
                    isChecked ? 'border-mint/30 bg-mint-soft' : 'border-obsidian-border bg-obsidian-elevated/40 hover:border-ember/30'
                  }`}
                >
                  <div className={`text-sm font-medium ${isChecked ? 'text-mint line-through' : 'text-ink'}`}>{cause}</div>
                  <div className="mt-1 flex items-start gap-1.5 text-xs text-ink-faint">
                    <span className="mt-px shrink-0 text-ember/70">→</span>
                    <span>{actions[i]}</span>
                  </div>
                </button>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

function TableMatchBlock({ match }: { match: TroubleshootingTableMatch }) {
  return (
    <div>
      <FlowTree root={match.symptom} causes={match.possible_causes} actions={match.recommended_actions} />
      <SourceFooter page={match.source_pages[0]} />
    </div>
  )
}

function DiagnosisMatchBlock({ match }: { match: WeldDiagnosisMatch }) {
  return (
    <div>
      <FlowTree
        root={`${match.defect_name} — ${match.visual_description}`}
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
        <div className="mb-3 rounded-lg border border-amber/25 bg-amber-soft px-3 py-2 text-xs text-amber">
          No exact symptom match — showing the closest matches by meaning. Click a branch to mark it checked.
        </div>
      )}
      <div className="flex flex-col gap-6">
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
