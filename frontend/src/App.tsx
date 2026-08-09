import { useEffect, useRef, useState } from 'react'
import { useChat } from './hooks/useChat'
import { MessageBubble } from './components/MessageBubble'
import { Composer } from './components/Composer'
import { QuickPrompts } from './components/QuickPrompts'

function App() {
  const [conversationId] = useState(() => crypto.randomUUID())
  const { messages, isStreaming, sendMessage } = useChat(conversationId)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages])

  const isEmpty = messages.length === 0

  return (
    <div className="flex h-screen flex-col bg-neutral-50">
      <header className="flex items-center gap-3 border-b border-neutral-200 bg-white px-5 py-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-orange-500 text-lg font-bold text-white">V</div>
        <div>
          <div className="text-sm font-semibold text-neutral-900">Vulcan OmniPro 220</div>
          <div className="text-xs text-neutral-500">AI Welding Assistant</div>
        </div>
      </header>

      {isEmpty ? (
        <div className="flex flex-1 flex-col items-center justify-center gap-6 px-4">
          <div className="text-center">
            <div className="text-xl font-semibold text-neutral-800">How can I help with your welder?</div>
            <div className="mt-1 text-sm text-neutral-500">
              Ask a technical question, upload a photo, or try one of these:
            </div>
          </div>
          <QuickPrompts onPick={(p) => sendMessage(p)} />
        </div>
      ) : (
        <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-5">
          <div className="mx-auto flex max-w-3xl flex-col gap-4">
            {messages.map((m) => (
              <MessageBubble key={m.id} message={m} />
            ))}
          </div>
        </div>
      )}

      <div className="mx-auto w-full max-w-3xl">
        <Composer disabled={isStreaming} onSend={sendMessage} />
      </div>
    </div>
  )
}

export default App
