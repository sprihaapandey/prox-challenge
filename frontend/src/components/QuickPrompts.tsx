const PROMPTS = [
  { text: 'How do I set up TIG?', icon: '🔌' },
  { text: "What's the duty cycle at 200A on 240V?", icon: '⏱️' },
  { text: 'Why is my flux-core weld porous?', icon: '🛠️' },
  { text: 'Which polarity should I use?', icon: '⚡' },
  { text: 'Help me configure this welder.', icon: '⚙️' },
]

export function QuickPrompts({ onPick }: { onPick: (prompt: string) => void }) {
  return (
    <div className="mx-auto flex max-w-xl flex-wrap justify-center gap-2 px-2">
      {PROMPTS.map((p, i) => (
        <button
          key={p.text}
          onClick={() => onPick(p.text)}
          style={{ animationDelay: `${i * 60}ms` }}
          className="animate-fade-in-up rounded-full border border-obsidian-border bg-obsidian-panel px-3.5 py-2 text-sm text-ink-muted opacity-0 shadow-sm transition hover:border-ember/40 hover:bg-obsidian-elevated hover:text-ink"
        >
          <span className="mr-1.5">{p.icon}</span>
          {p.text}
        </button>
      ))}
    </div>
  )
}
