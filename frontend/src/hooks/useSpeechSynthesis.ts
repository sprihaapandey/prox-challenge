import { useCallback, useEffect, useState } from 'react'
import { stripMarkdown } from '../lib/stripMarkdown'

export function useSpeechSynthesis() {
  const [isSupported] = useState(() => typeof window !== 'undefined' && 'speechSynthesis' in window)
  const [speakingId, setSpeakingId] = useState<string | null>(null)

  useEffect(() => {
    if (!isSupported) return
    return () => window.speechSynthesis.cancel()
  }, [isSupported])

  const speak = useCallback(
    (id: string, text: string) => {
      if (!isSupported) return
      window.speechSynthesis.cancel()
      const utterance = new SpeechSynthesisUtterance(stripMarkdown(text))
      utterance.rate = 1.02
      utterance.onend = () => setSpeakingId((cur) => (cur === id ? null : cur))
      utterance.onerror = () => setSpeakingId((cur) => (cur === id ? null : cur))
      setSpeakingId(id)
      window.speechSynthesis.speak(utterance)
    },
    [isSupported],
  )

  const stop = useCallback(() => {
    if (!isSupported) return
    window.speechSynthesis.cancel()
    setSpeakingId(null)
  }, [isSupported])

  return { isSupported, speakingId, speak, stop }
}
