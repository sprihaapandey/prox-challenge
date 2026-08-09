import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { ChatMessage } from '../types'
import { ToolStatusList } from './ToolStatus'

export function MessageBubble({ message }: { message: ChatMessage }) {
  if (message.role === 'user') {
    return (
      <div className="flex justify-end">
        <div className="max-w-[75%]">
          {message.images && message.images.length > 0 && (
            <div className="mb-1.5 flex justify-end gap-2">
              {message.images.map((url, i) => (
                <img key={i} src={url} alt="attachment" className="h-24 w-24 rounded-lg object-cover border border-neutral-200" />
              ))}
            </div>
          )}
          <div className="rounded-2xl rounded-br-sm bg-neutral-900 px-4 py-2.5 text-[15px] leading-relaxed text-white">
            {message.text}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex justify-start">
      <div className="max-w-[85%]">
        <ToolStatusList toolCalls={message.toolCalls ?? []} />
        {message.text ? (
          <div className="prose-chat rounded-2xl rounded-bl-sm bg-white px-4 py-2.5 text-[15px] leading-relaxed text-neutral-800 border border-neutral-100 shadow-sm">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.text}</ReactMarkdown>
          </div>
        ) : message.streaming ? (
          <div className="flex items-center gap-1 rounded-2xl rounded-bl-sm bg-white px-4 py-3 border border-neutral-100 shadow-sm w-fit">
            <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-neutral-300 [animation-delay:-0.3s]" />
            <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-neutral-300 [animation-delay:-0.15s]" />
            <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-neutral-300" />
          </div>
        ) : null}
      </div>
    </div>
  )
}
