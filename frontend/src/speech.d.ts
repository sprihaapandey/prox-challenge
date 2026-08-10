// Minimal ambient types for the Web Speech API (not yet in standard TS DOM lib).

interface SpeechRecognitionEventResult {
  transcript: string
}

interface SpeechRecognitionResultLike {
  0: SpeechRecognitionEventResult
  isFinal: boolean
}

interface SpeechRecognitionEvent extends Event {
  resultIndex: number
  results: ArrayLike<SpeechRecognitionResultLike>
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string
}

interface SpeechRecognition extends EventTarget {
  lang: string
  continuous: boolean
  interimResults: boolean
  onresult: ((event: SpeechRecognitionEvent) => void) | null
  onerror: ((event: SpeechRecognitionErrorEvent) => void) | null
  onend: (() => void) | null
  start: () => void
  stop: () => void
  abort: () => void
}

interface Window {
  SpeechRecognition?: new () => SpeechRecognition
  webkitSpeechRecognition?: new () => SpeechRecognition
}
