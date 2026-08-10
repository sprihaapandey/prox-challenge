export const DOC_META: Record<string, { title: string; pageCount: number }> = {
  'owner-manual': { title: "Owner's Manual", pageCount: 48 },
  'quick-start-guide': { title: 'Quick Start Guide', pageCount: 2 },
  'selection-chart': { title: 'Welder Selection Chart', pageCount: 1 },
}

export function docTitle(docId: string): string {
  return DOC_META[docId]?.title ?? docId
}

export function docPageCount(docId: string): number {
  return DOC_META[docId]?.pageCount ?? 1
}
