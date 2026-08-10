import type { Artifact } from '../../types'
import { PolarityDiagram } from './PolarityDiagram'
import { DutyCycleCalculator } from './DutyCycleCalculator'
import { TroubleshootingFlowchart } from './TroubleshootingFlowchart'
import { SettingsConfigurator } from './SettingsConfigurator'

export function ArtifactRenderer({ artifact }: { artifact: Artifact }) {
  switch (artifact.artifact_type) {
    case 'polarity_diagram':
      return <PolarityDiagram records={artifact.data.records} highlight={artifact.data.highlight} />
    case 'duty_cycle_calculator':
      return <DutyCycleCalculator records={artifact.data.records} highlight={artifact.data.highlight} />
    case 'troubleshooting_flowchart':
      return (
        <TroubleshootingFlowchart
          matchType={artifact.data.match_type}
          tableMatches={artifact.data.table_matches}
          diagnosisMatches={artifact.data.diagnosis_matches}
        />
      )
    case 'settings_configurator':
      return (
        <SettingsConfigurator
          capabilities={artifact.data.capabilities}
          importantCaveat={artifact.data.important_caveat}
          highlight={artifact.data.highlight}
        />
      )
    default:
      return null
  }
}
