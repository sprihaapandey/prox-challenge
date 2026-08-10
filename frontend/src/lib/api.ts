export type ChatEvent =
  | { type: 'text_delta'; text: string }
  | { type: 'tool_call'; id: string; name: string; input: Record<string, unknown> }
  | { type: 'tool_result'; tool_use_id: string; name: string; is_error: boolean; evidence: unknown[]; artifact: unknown | null }
  | { type: 'done'; result: string | null; cost_usd: number | null }
  | { type: 'error'; message: string }

export async function* streamChat(
  conversationId: string,
  message: string,
  imagePaths: string[] | undefined,
  signal: AbortSignal,
): AsyncGenerator<ChatEvent> {
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ conversation_id: conversationId, message, image_paths: imagePaths }),
    signal,
  })
  if (!res.body) throw new Error('No response body')

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    let sepIndex: number
    while ((sepIndex = buffer.indexOf('\n\n')) !== -1) {
      const rawEvent = buffer.slice(0, sepIndex)
      buffer = buffer.slice(sepIndex + 2)

      let eventType = 'message'
      let data = ''
      for (const line of rawEvent.split('\n')) {
        if (line.startsWith('event: ')) eventType = line.slice(7)
        else if (line.startsWith('data: ')) data = line.slice(6)
      }
      if (!data) continue
      yield { type: eventType, ...JSON.parse(data) } as ChatEvent
    }
  }
}

export async function uploadImage(file: File): Promise<{ path: string; url: string }> {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch('/api/upload', { method: 'POST', body: form })
  if (!res.ok) throw new Error('Upload failed')
  return res.json()
}

export async function endConversation(conversationId: string): Promise<void> {
  await fetch(`/api/conversation/${conversationId}`, { method: 'DELETE' })
}
