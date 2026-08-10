import { useEffect, useRef, useState } from 'react'
import { useChat } from './hooks/useChat'
import { useSpeechSynthesis } from './hooks/useSpeechSynthesis'
import { MessageBubble } from './components/MessageBubble'
import { Composer } from './components/Composer'
import { QuickPrompts } from './components/QuickPrompts'
import { ManualViewerModal } from './components/ManualViewerModal'
import { ManualViewerProvider } from './context/ManualViewerContext'
import { VisualsPanel, EmptyVisualsPanel } from './components/VisualsPanel'

const SIDE_PANEL_WIDTH = 'w-[400px]'

function AppShell() {
  const [conversationId] = useState(() => crypto.randomUUID())
  const { messages, isStreaming, sendMessage } = useChat(conversationId)
  const speech = useSpeechSynthesis()
  const scrollRef = useRef<HTMLDivElement>(null)
  const lastMessageRef = useRef<HTMLDivElement>(null)
  const wasLastStreamingRef = useRef(false)

  useEffect(() => {
    const lastMessage = messages[messages.length - 1]
    const isLastStreaming = lastMessage?.streaming ?? false

    if (isLastStreaming) {
      // Text actively growing — follow the bottom as it streams.
      scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
    } else if (wasLastStreamingRef.current) {
      // Just finished: on narrow viewports the artifact/sources are about to
      // append inline below the text. Reveal the message from its own top
      // instead of snapping to the container's absolute bottom, which
      // overshoots past the artifact once it's taller than the viewport.
      // (On wide viewports this doesn't matter — the side panel is a
      // separate scroll container and never affects this one's height.)
      lastMessageRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
    wasLastStreamingRef.current = isLastStreaming
  }, [messages])

  const isEmpty = messages.length === 0
  const latestAssistant = [...messages].reverse().find((m) => m.role === 'assistant')
  const sidePanelToolCalls = latestAssistant?.toolCalls ?? []

  return (
    <div className="flex h-dvh flex-col bg-obsidian">
      <header className="relative flex shrink-0 items-center gap-3 border-b border-obsidian-border bg-obsidian-panel/80 px-4 py-3 backdrop-blur sm:px-5">
        <div className="relative flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-ember to-ember-dim text-base font-bold text-white shadow-[0_0_20px_var(--color-ember-glow)]">
          {isStreaming && <span className="absolute -inset-1 -z-10 animate-ping rounded-xl bg-ember/40" />}
          V
        </div>
        <div className="min-w-0">
          <div className="truncate text-sm font-semibold tracking-tight text-ink">Vulcan OmniPro 220</div>
          <div className="truncate text-xs text-ink-faint">AI Welding Assistant</div>
        </div>
      </header>

      {isEmpty ? (
        <div className="relative flex flex-1 flex-col items-center justify-center gap-7 overflow-hidden px-4">
          <div
            className="pointer-events-none absolute left-1/2 top-1/2 h-[420px] w-[420px] -translate-x-1/2 -translate-y-1/2 rounded-full opacity-60 blur-3xl"
            style={{ background: 'radial-gradient(circle, var(--color-ember-soft), transparent 70%)' }}
          />
          <div className="relative text-center animate-fade-in-up">
            <div className="text-2xl font-semibold tracking-tight text-ink sm:text-[28px]">How can I help with your welder?</div>
            <div className="mt-2 text-sm text-ink-muted">Ask a technical question, upload a photo, or try one of these:</div>
          </div>
          <div className="relative w-full">
            <QuickPrompts onPick={(p) => sendMessage(p)} />
          </div>
        </div>
      ) : (
        <div className="flex flex-1 overflow-hidden">
          <div ref={scrollRef} className="flex-1 overflow-y-auto px-3 py-5 sm:px-4">
            <div className="mx-auto flex max-w-3xl flex-col gap-5">
              {messages.map((m, i) => (
                <div key={m.id} ref={i === messages.length - 1 ? lastMessageRef : undefined}>
                  <MessageBubble message={m} speech={speech} />
                </div>
              ))}
            </div>
          </div>

          {/* Persistent workspace for the latest turn's diagrams/calculators/
           * sources — a separate scroll container from the chat column, so
           * populating it never reflows or buries the text being read.
           * Hidden below xl; MessageBubble renders the same content inline
           * there instead (see its xl:hidden block). */}
          <aside className={`hidden shrink-0 overflow-y-auto border-l border-obsidian-border p-4 xl:block ${SIDE_PANEL_WIDTH}`}>
            {sidePanelToolCalls.length > 0 ? <VisualsPanel toolCalls={sidePanelToolCalls} /> : <EmptyVisualsPanel />}
          </aside>
        </div>
      )}

      <div className="flex shrink-0">
        <div className="mx-auto w-full max-w-3xl flex-1">
          <Composer disabled={isStreaming} onSend={sendMessage} />
        </div>
        {!isEmpty && <div className={`hidden shrink-0 border-l border-obsidian-border xl:block ${SIDE_PANEL_WIDTH}`} />}
      </div>
    </div>
  )
}

function App() {
  return (
    <ManualViewerProvider>
      <AppShell />
      <ManualViewerModal />
    </ManualViewerProvider>
  )
}

export default App
