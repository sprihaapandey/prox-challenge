import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react'

export interface ManualViewerState {
  docId: string
  page: number
  highlightBboxPct?: [number, number, number, number] | null
}

interface ManualViewerContextValue {
  state: ManualViewerState | null
  openPage: (docId: string, page: number, highlightBboxPct?: [number, number, number, number] | null) => void
  close: () => void
}

const ManualViewerContext = createContext<ManualViewerContextValue | null>(null)

export function ManualViewerProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<ManualViewerState | null>(null)

  const openPage = useCallback(
    (docId: string, page: number, highlightBboxPct?: [number, number, number, number] | null) => {
      setState({ docId, page, highlightBboxPct })
    },
    [],
  )
  const close = useCallback(() => setState(null), [])

  const value = useMemo(() => ({ state, openPage, close }), [state, openPage, close])

  return <ManualViewerContext.Provider value={value}>{children}</ManualViewerContext.Provider>
}

export function useManualViewer(): ManualViewerContextValue {
  const ctx = useContext(ManualViewerContext)
  if (!ctx) throw new Error('useManualViewer must be used within ManualViewerProvider')
  return ctx
}
