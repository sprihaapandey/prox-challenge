import type { ReactNode } from 'react'
import { useManualViewer } from '../../context/ManualViewerContext'

export function ArtifactCard({ title, icon, children }: { title: string; icon: string; children: ReactNode }) {
  return (
    <div className="w-full max-w-xl overflow-hidden rounded-2xl border border-obsidian-border bg-gradient-to-b from-obsidian-panel to-obsidian-panel/70 shadow-[0_8px_30px_rgba(0,0,0,0.35)]">
      <div className="flex items-center gap-2 border-b border-obsidian-border bg-obsidian-elevated/50 px-4 py-2.5">
        <span className="text-base leading-none">{icon}</span>
        <span className="text-sm font-semibold text-ink">{title}</span>
      </div>
      <div className="p-4">{children}</div>
    </div>
  )
}

export function SourceFooter({ page, docId = 'owner-manual' }: { page: number; docId?: string }) {
  const { openPage } = useManualViewer()
  return (
    <div className="mt-3 flex items-center justify-between border-t border-obsidian-border pt-2.5 text-xs text-ink-faint">
      <span>Manual — Page {page}</span>
      <button onClick={() => openPage(docId, page)} className="font-medium text-ember transition hover:text-ember/80">
        View original page →
      </button>
    </div>
  )
}
