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
      highlight_bbox_pct: [number, number, number, number] | null
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

export interface DutyCycleRecord {
  process: string
  input_voltage: number
  amperage: number
  duty_cycle_percent: number
  welding_current_range: string
  source_page: number
}

export interface PolarityRecord {
  process: string
  polarity_name: string
  polarity_full_name: string
  gun_or_torch_or_electrode_cable: string
  gun_or_torch_or_electrode_socket: 'Positive' | 'Negative'
  ground_clamp_socket: 'Positive' | 'Negative'
  applies_to: string
  source_page: number
}

export interface SettingsCapability {
  process: string
  wire_type?: string
  wire_diameters?: string[]
  rod_or_electrode?: string
  electrode_types_shown_on_lcd?: string[]
  gas: string
  gas_flow_scfh_range?: string
  polarity?: string
  weldable_materials?: string[]
  source_page: number
}

export interface TroubleshootingTableMatch {
  process: string
  symptom: string
  possible_causes: string[]
  recommended_actions: string[]
  source_pages: number[]
  relevance?: number
}

export interface WeldDiagnosisMatch {
  process: string
  defect_name: string
  visual_description: string
  possible_causes_and_solutions: { cause: string; solution: string }[]
  source_page: number
  relevance?: number
}

export type Artifact =
  | {
      artifact_type: 'duty_cycle_calculator'
      title: string
      data: { records: DutyCycleRecord[]; highlight: { process: string; input_voltage: number; amperage: number } | null }
    }
  | {
      artifact_type: 'polarity_diagram'
      title: string
      data: { records: PolarityRecord[]; highlight: string | null }
    }
  | {
      artifact_type: 'settings_configurator'
      title: string
      data: { capabilities: SettingsCapability[]; important_caveat: string; highlight: string | null }
    }
  | {
      artifact_type: 'troubleshooting_flowchart'
      title: string
      data: { match_type: 'exact' | 'semantic'; table_matches: TroubleshootingTableMatch[]; diagnosis_matches: WeldDiagnosisMatch[] }
    }

export interface ToolCall {
  id: string
  name: string
  input: Record<string, unknown>
  status: 'running' | 'done' | 'error'
  evidence: EvidenceItem[]
  artifact?: Artifact | null
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  text: string
  images?: string[] // image urls attached by the user
  toolCalls?: ToolCall[]
  streaming?: boolean
  error?: string
}
