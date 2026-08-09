import { useCallback, useRef, useState } from 'react'
import { streamChat } from '../lib/api'
import type { ChatMessage, EvidenceItem, ToolCall } from '../types'

function newId(): string {
  return Math.random().toString(36).slice(2) + Date.now().toString(36)
}

export function useChat(conversationId: string) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isStreaming, setIsStreaming] = useState(false)
  const abortRef = useRef<AbortController | null>(null)

  const updateLastAssistant = useCallback((fn: (m: ChatMessage) => ChatMessage) => {
    setMessages((prev) => {
      const next = [...prev]
      const lastIdx = next.length - 1
      if (lastIdx >= 0 && next[lastIdx].role === 'assistant') {
        next[lastIdx] = fn(next[lastIdx])
      }
      return next
    })
  }, [])

  const sendMessage = useCallback(
    async (text: string, imagePaths?: string[], imageUrls?: string[]) => {
      const userMsg: ChatMessage = { id: newId(), role: 'user', text, images: imageUrls }
      const assistantMsg: ChatMessage = { id: newId(), role: 'assistant', text: '', toolCalls: [], streaming: true }
      setMessages((prev) => [...prev, userMsg, assistantMsg])
      setIsStreaming(true)

      const controller = new AbortController()
      abortRef.current = controller

      try {
        for await (const event of streamChat(conversationId, text, imagePaths, controller.signal)) {
          if (event.type === 'text_delta') {
            updateLastAssistant((m) => ({ ...m, text: m.text + event.text }))
          } else if (event.type === 'tool_call') {
            const call: ToolCall = { id: event.id, name: event.name, input: event.input, status: 'running', evidence: [] }
            updateLastAssistant((m) => ({ ...m, toolCalls: [...(m.toolCalls ?? []), call] }))
          } else if (event.type === 'tool_result') {
            updateLastAssistant((m) => ({
              ...m,
              toolCalls: (m.toolCalls ?? []).map((c) =>
                c.id === event.tool_use_id
                  ? { ...c, status: event.is_error ? 'error' : 'done', evidence: event.evidence as EvidenceItem[] }
                  : c,
              ),
            }))
          } else if (event.type === 'error') {
            updateLastAssistant((m) => ({ ...m, text: m.text + `\n\n_Error: ${event.message}_` }))
          } else if (event.type === 'done') {
            updateLastAssistant((m) => ({ ...m, streaming: false }))
          }
        }
      } catch (err) {
        if ((err as Error).name !== 'AbortError') {
          updateLastAssistant((m) => ({ ...m, text: m.text + `\n\n_Connection error: ${(err as Error).message}_`, streaming: false }))
        }
      } finally {
        setIsStreaming(false)
      }
    },
    [conversationId, updateLastAssistant],
  )

  const stop = useCallback(() => {
    abortRef.current?.abort()
  }, [])

  return { messages, isStreaming, sendMessage, stop }
}
