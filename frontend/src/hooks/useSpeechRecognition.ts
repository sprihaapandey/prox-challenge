import { useCallback, useEffect, useRef, useState } from 'react'

export function useSpeechRecognition() {
  const [isSupported] = useState(() => typeof window !== 'undefined' && !!(window.SpeechRecognition || window.webkitSpeechRecognition))
  const [isListening, setIsListening] = useState(false)
  const [interimTranscript, setInterimTranscript] = useState('')
  const recognitionRef = useRef<SpeechRecognition | null>(null)
  const onFinalRef = useRef<((text: string) => void) | null>(null)

  useEffect(() => {
    if (!isSupported) return
    const Ctor = window.SpeechRecognition ?? window.webkitSpeechRecognition!
    const recognition = new Ctor()
    recognition.lang = 'en-US'
    recognition.continuous = true
    recognition.interimResults = true

    recognition.onresult = (event) => {
      let interim = ''
      let final = ''
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i]
        if (result.isFinal) final += result[0].transcript
        else interim += result[0].transcript
      }
      if (final) onFinalRef.current?.(final)
      setInterimTranscript(interim)
    }
    recognition.onerror = () => setIsListening(false)
    recognition.onend = () => setIsListening(false)

    recognitionRef.current = recognition
    return () => recognition.abort()
  }, [isSupported])

  const start = useCallback((onFinal: (text: string) => void) => {
    if (!recognitionRef.current) return
    onFinalRef.current = onFinal
    setInterimTranscript('')
    setIsListening(true)
    recognitionRef.current.start()
  }, [])

  const stop = useCallback(() => {
    recognitionRef.current?.stop()
    setIsListening(false)
  }, [])

  return { isSupported, isListening, interimTranscript, start, stop }
}
