import type { ToolCall } from '../types'
import { toolLabel } from '../lib/toolLabels'
import { EvidenceCard } from './EvidenceCard'

function StatusDot({ status }: { status: ToolCall['status'] }) {
  if (status === 'running') {
    return <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-orange-500" />
  }
  if (status === 'error') {
    return <span className="h-1.5 w-1.5 rounded-full bg-red-500" />
  }
  return <span className="h-1.5 w-1.5 rounded-full bg-green-600" />
}

export function ToolStatusList({ toolCalls }: { toolCalls: ToolCall[] }) {
  if (toolCalls.length === 0) return null
  const allEvidence = toolCalls.flatMap((c) => c.evidence)

  return (
    <div className="mb-2 flex flex-col gap-2">
      <div className="flex flex-wrap gap-1.5">
        {toolCalls.map((c) => (
          <div
            key={c.id}
            className="flex items-center gap-1.5 rounded-full border border-neutral-200 bg-neutral-50 px-2.5 py-1 text-xs text-neutral-600"
          >
            <StatusDot status={c.status} />
            {toolLabel(c.name, c.status)}
          </div>
        ))}
      </div>
      {allEvidence.length > 0 && (
        <div className="flex gap-2 overflow-x-auto pb-1">
          {allEvidence.map((item, i) => (
            <EvidenceCard key={i} item={item} />
          ))}
        </div>
      )}
    </div>
  )
}
