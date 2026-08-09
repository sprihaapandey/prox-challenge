import type { ToolCall } from '../types'
import { toolLabel } from '../lib/toolLabels'

function StatusDot({ status }: { status: ToolCall['status'] }) {
  if (status === 'running') {
    return <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-orange-500" />
  }
  if (status === 'error') {
    return <span className="h-1.5 w-1.5 rounded-full bg-red-500" />
  }
  return <span className="h-1.5 w-1.5 rounded-full bg-green-600" />
}

/** Live progress indicators shown while the agent is working. Lightweight by
 * design — the actual evidence (manual pages/diagrams) is deferred to
 * SourcesPanel until the response finishes, so it reads as citations rather
 * than a noisy live feed. */
export function ToolStatusPills({ toolCalls }: { toolCalls: ToolCall[] }) {
  if (toolCalls.length === 0) return null

  return (
    <div className="mb-2 flex flex-wrap gap-1.5">
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
  )
}
