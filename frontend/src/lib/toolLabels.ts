const LABELS: Record<string, { running: string; done: string }> = {
  search_manual: { running: 'Searching the manual…', done: 'Searched the manual' },
  search_visuals: { running: 'Looking for diagrams…', done: 'Found diagrams' },
  lookup_duty_cycle: { running: 'Checking duty cycle chart…', done: 'Checked duty cycle chart' },
  lookup_polarity: { running: 'Checking polarity setup…', done: 'Checked polarity setup' },
  lookup_settings: { running: 'Checking settings capabilities…', done: 'Checked settings' },
  troubleshoot: { running: 'Checking troubleshooting guide…', done: 'Checked troubleshooting guide' },
  lookup_part: { running: 'Looking up part…', done: 'Looked up part' },
  get_manual_page: { running: 'Opening manual page…', done: 'Opened manual page' },
}

export function shortToolName(fullName: string): string {
  return fullName.replace(/^mcp__omnipro__/, '')
}

export function toolLabel(fullName: string, status: 'running' | 'done' | 'error'): string {
  const short = shortToolName(fullName)
  const entry = LABELS[short]
  if (!entry) return short
  if (status === 'error') return `Couldn't complete: ${entry.done.toLowerCase()}`
  return status === 'running' ? entry.running : entry.done
}
