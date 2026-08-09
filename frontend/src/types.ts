export type EvidenceItem =
  | {
      type: 'page_reference'
      doc_id: string
      page: number
      section: string | null
      snippet: string
      relevance: number | null
    }
  | {
      type: 'visual'
      id: string
      doc_id: string
      page: number
      visual_type: string
      title: string
      description: string
      image_url: string
      relevance: number | null
    }
  | {
      type: 'page_image'
      doc_id: string
      page: number
      section: string | null
      image_url: string
    }
  | {
      type: 'fact'
      fact_kind: 'duty_cycle' | 'polarity' | 'settings' | 'part'
      doc_id: string
      page: number | null
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      data: any
    }

export interface ToolCall {
  id: string
  name: string
  input: Record<string, unknown>
  status: 'running' | 'done' | 'error'
  evidence: EvidenceItem[]
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  text: string
  images?: string[] // image urls attached by the user
  toolCalls?: ToolCall[]
  streaming?: boolean
}
