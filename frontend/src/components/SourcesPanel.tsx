import type { ToolCall } from '../types'
import { EvidenceCard } from './EvidenceCard'

/** Citations for a completed response. Rendered only once the message has
 * finished streaming, so sources land after the answer like a reference
 * list rather than popping in mid-generation. */
export function SourcesPanel({ toolCalls }: { toolCalls: ToolCall[] }) {
  const allEvidence = toolCalls.flatMap((c) => c.evidence)
  if (allEvidence.length === 0) return null

  return (
    <div className="mt-2">
      <div className="mb-1.5 text-[11px] font-medium uppercase tracking-wide text-ink-faint">Sources</div>
      <div className="flex gap-2 overflow-x-auto pb-1">
        {allEvidence.map((item, i) => (
          <EvidenceCard key={i} item={item} />
        ))}
      </div>
    </div>
  )
}
