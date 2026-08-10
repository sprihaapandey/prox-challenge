import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { ChatMessage } from '../types'
import type { useSpeechSynthesis } from '../hooks/useSpeechSynthesis'
import { ToolStatusPills } from './ToolStatus'
import { VisualsPanel } from './VisualsPanel'

type Speech = ReturnType<typeof useSpeechSynthesis>

function TypingIndicator() {
  return (
    <div className="flex w-fit items-center gap-1.5 rounded-2xl rounded-bl-sm border border-obsidian-border bg-obsidian-panel px-4 py-3.5">
      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-ember [animation-delay:-0.3s]" />
      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-ember [animation-delay:-0.15s]" />
      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-ember" />
    </div>
  )
}

function ErrorBanner({ message }: { message: string }) {
  return (
    <div className="flex items-start gap-2.5 rounded-2xl rounded-bl-sm border border-rose/30 bg-rose-soft px-4 py-3 text-sm text-rose">
      <span className="mt-0.5">⚠</span>
      <div>
        <div className="font-medium">Something went wrong</div>
        <div className="mt-0.5 text-rose/80">{message}</div>
      </div>
    </div>
  )
}

function SpeakButton({ message, speech }: { message: ChatMessage; speech: Speech }) {
  if (!speech.isSupported || !message.text) return null
  const isSpeaking = speech.speakingId === message.id
  return (
    <button
      onClick={() => (isSpeaking ? speech.stop() : speech.speak(message.id, message.text))}
      className={`mt-1.5 flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs transition ${
        isSpeaking
          ? 'border-ember/40 bg-ember-soft text-ember'
          : 'border-obsidian-border text-ink-faint hover:border-obsidian-border-strong hover:text-ink-muted'
      }`}
      aria-label={isSpeaking ? 'Stop reading aloud' : 'Read aloud'}
    >
      {isSpeaking ? '◼ Stop' : '🔊 Listen'}
    </button>
  )
}

export function MessageBubble({ message, speech }: { message: ChatMessage; speech: Speech }) {
  if (message.role === 'user') {
    return (
      <div className="flex justify-end animate-fade-in-up">
        <div className="max-w-[85%] sm:max-w-[75%]">
          {message.images && message.images.length > 0 && (
            <div className="mb-1.5 flex justify-end gap-2">
              {message.images.map((url, i) => (
                <img key={i} src={url} alt="attachment" className="h-24 w-24 rounded-lg border border-obsidian-border object-cover" />
              ))}
            </div>
          )}
          <div className="rounded-2xl rounded-br-sm bg-ink px-4 py-2.5 text-[15px] leading-relaxed text-obsidian">
            {message.text}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex justify-start animate-fade-in-up">
      <div className="w-full max-w-[92%] sm:max-w-[85%]">
        <ToolStatusPills toolCalls={message.toolCalls ?? []} />

        {message.text ? (
          <div className="prose-chat rounded-2xl rounded-bl-sm border border-obsidian-border bg-obsidian-panel px-4 py-3 text-ink shadow-[0_1px_0_rgba(255,255,255,0.03)_inset]">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.text}</ReactMarkdown>
          </div>
        ) : message.streaming ? (
          <TypingIndicator />
        ) : null}
        {message.error && <div className="mt-2"><ErrorBanner message={message.error} /></div>}
        {!message.streaming && message.text && <SpeakButton message={message} speech={speech} />}

        {/* Desktop shows artifacts/sources in the persistent side panel
         * (App.tsx) instead — this inline copy only renders on narrow
         * viewports where there's no room for a side column. Still gated on
         * !streaming there since, inline, popping it in mid-stream would
         * reflow the text above it exactly like before. */}
        {!message.streaming && (
          <div className="mt-3 animate-fade-in-up xl:hidden">
            <VisualsPanel toolCalls={message.toolCalls ?? []} />
          </div>
        )}
      </div>
    </div>
  )
}
