import type { ToolCall } from '../types'
import { ArtifactRenderer } from './artifacts/ArtifactRenderer'
import { SourcesPanel } from './SourcesPanel'

/** Artifacts + sources for one turn, decoupled from the text bubble. Used
 * both as the persistent desktop side panel (always reflects the latest
 * turn, updates live as tool calls resolve — a separate scroll container,
 * so it can never shove the text column around) and, on mobile where there's
 * no room for a side column, inline beneath each message's text instead. */
export function VisualsPanel({ toolCalls }: { toolCalls: ToolCall[] }) {
  const artifactCalls = toolCalls.filter((c) => c.artifact)
  const hasEvidence = toolCalls.some((c) => c.evidence.length > 0)

  if (artifactCalls.length === 0 && !hasEvidence) return null

  return (
    <div className="flex flex-col gap-3">
      {artifactCalls.map((c) => (
        <ArtifactRenderer key={c.id} artifact={c.artifact!} />
      ))}
      <SourcesPanel toolCalls={toolCalls} />
    </div>
  )
}

export function EmptyVisualsPanel() {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-2 text-center text-ink-faint">
      <span className="text-2xl">📎</span>
      <div className="text-sm">Diagrams, calculators, and sources will appear here</div>
    </div>
  )
}
