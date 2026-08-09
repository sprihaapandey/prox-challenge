const PROMPTS = [
  'How do I set up TIG?',
  "What's the duty cycle at 200A on 240V?",
  'Why is my flux-core weld porous?',
  'Which polarity should I use?',
  'Help me configure this welder.',
]

export function QuickPrompts({ onPick }: { onPick: (prompt: string) => void }) {
  return (
    <div className="flex flex-wrap justify-center gap-2">
      {PROMPTS.map((p) => (
        <button
          key={p}
          onClick={() => onPick(p)}
          className="rounded-full border border-neutral-200 bg-white px-3.5 py-1.5 text-sm text-neutral-600 shadow-sm transition hover:border-orange-300 hover:text-orange-700"
        >
          {p}
        </button>
      ))}
    </div>
  )
}
