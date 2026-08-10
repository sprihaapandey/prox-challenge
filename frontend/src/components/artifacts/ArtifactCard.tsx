import type { ReactNode } from 'react'
import { useManualViewer } from '../../context/ManualViewerContext'

export function ArtifactCard({ title, icon, children }: { title: string; icon: string; children: ReactNode }) {
  return (
    <div className="w-full max-w-xl overflow-hidden rounded-2xl border border-neutral-200 bg-white shadow-sm">
      <div className="flex items-center gap-2 border-b border-neutral-100 bg-neutral-50 px-4 py-2.5">
        <span className="text-base leading-none">{icon}</span>
        <span className="text-sm font-semibold text-neutral-700">{title}</span>
      </div>
      <div className="p-4">{children}</div>
    </div>
  )
}

export function SourceFooter({ page, docId = 'owner-manual' }: { page: number; docId?: string }) {
  const { openPage } = useManualViewer()
  return (
    <div className="mt-3 flex items-center justify-between border-t border-neutral-100 pt-2.5 text-xs text-neutral-500">
      <span>
        Manual — Page {page}
      </span>
      <button onClick={() => openPage(docId, page)} className="font-medium text-orange-600 hover:text-orange-700">
        View original page →
      </button>
    </div>
  )
}
