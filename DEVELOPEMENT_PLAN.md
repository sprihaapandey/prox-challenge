# Prox Engineering Challenge — Vulcan OmniPro 220 Multimodal Agent

## 1. Mission

Build a polished, production-quality multimodal technical support agent for the **Vulcan OmniPro 220** welding machine.

The agent must use the **Anthropic Claude Agent SDK** as its reasoning/agent foundation and must run locally with a single API key provided through `.env`.

The goal is **not** to build a generic PDF chatbot.

The goal is to build an expert-like interactive assistant that can:

1. Answer technically difficult questions accurately.
2. Ground answers in the provided Vulcan OmniPro 220 manuals.
3. Cross-reference multiple sections of the manual.
4. Understand information contained in tables, diagrams, schematics, and images.
5. Surface relevant manual visuals when appropriate.
6. Generate useful visual explanations when text is insufficient.
7. Create interactive artifacts such as calculators, configurators, and troubleshooting flows.
8. Ask clarifying questions when the user's request is ambiguous.
9. Clearly distinguish verified manual information from general advice.
10. Provide source/page references for important technical claims.

The experience should feel like:

> "I just bought this welder and an expert is standing beside me helping me use it."

---

# 2. Challenge Requirements

The agent will be evaluated on:

### Technical accuracy

It must correctly answer questions such as:

* "What's the duty cycle for MIG welding at 200A on 240V?"
* "I'm getting porosity in my flux-cored welds. What should I check?"
* "What polarity setup do I need for TIG welding?"
* "Which socket does the ground clamp go in?"

Questions may require cross-referencing:

* duty-cycle matrices
* process-specific instructions
* voltage/amperage tables
* polarity configurations
* wire-feed mechanisms
* troubleshooting matrices
* weld diagnosis diagrams
* wiring schematics
* parts diagrams

### Multimodal responses

The agent must NOT be text-only.

When appropriate, it should:

* display the relevant manual image
* display a diagram
* generate a visual explanation
* create an interactive calculator
* create a troubleshooting flowchart
* create a settings configurator
* allow users to inspect the relevant manual page

### Tone

The user should feel supported rather than overwhelmed.

Use clear language appropriate for someone who is technically capable but may not be a professional welder.

### Knowledge extraction

Critical information may exist only inside:

* diagrams
* charts
* tables
* schematics
* photographs
* decision matrices

The system must therefore preserve and index visual information rather than relying exclusively on text extraction.

---

# 3. Product Vision

The final experience should look approximately like:

```text
┌──────────────────────────────────────────────────────┐
│                  VULCAN OMNIPRO 220                  │
│                  AI Welding Assistant                │
├──────────────────────────────────────────────────────┤
│                                                      │
│ User: How do I set up TIG?                           │
│                                                      │
│ Assistant:                                           │
│                                                      │
│ For TIG, connect the torch and work clamp according  │
│ to the polarity configuration shown below.           │
│                                                      │
│ ┌──────────────────────────────────────────────┐     │
│ │              TIG SETUP DIAGRAM               │     │
│ │                                              │     │
│ │       TIG TORCH ───────► [ SOCKET ]          │     │
│ │                                              │     │
│ │       WORK CLAMP ──────► [ SOCKET ]          │     │
│ │                                              │     │
│ └──────────────────────────────────────────────┘     │
│                                                      │
│ 📖 Manual — Page XX                                  │
│ [View source diagram]                                │
│                                                      │
├──────────────────────────────────────────────────────┤
│ Ask about your welder...                       [🎤] │
└──────────────────────────────────────────────────────┘
```

The UI does not have to match this exactly.

Prioritize usability, clarity, and polish.

---

# 4. Core Architectural Principle

Do NOT build:

```text
User → LLM → PDF chunks → Answer
```

Build:

```text
User
  ↓
Claude Agent
  ↓
Tool selection
  ↓
┌─────────────────────────────────────┐
│ Manual Search                       │
│ Visual Search                       │
│ Structured Fact Lookup              │
│ Duty Cycle Lookup                   │
│ Polarity Lookup                     │
│ Troubleshooting                     │
│ Artifact Generation                 │
└─────────────────────────────────────┘
  ↓
Evidence
  ↓
Claude reasoning
  ↓
Response + Sources + Artifact
  ↓
Frontend renderer
```

The LLM should be able to **interrogate the knowledge base** rather than simply receiving a large collection of retrieved text.

---

# 5. Recommended Technology

Use the following unless there is a strong technical reason to change something.

## Backend

* Python
* FastAPI
* Anthropic Claude Agent SDK
* PostgreSQL
* pgvector or equivalent vector search
* Python PDF/document processing libraries

## Frontend

* React
* TypeScript
* Vite or equivalent
* Modern CSS / Tailwind if useful

## Infrastructure

The project must run locally.

A developer should be able to do approximately:

```bash
git clone ...
cd ...
cp .env.example .env
# add ANTHROPIC_API_KEY
npm install
pip install -r requirements.txt
npm run dev
```

or an equivalent simple startup process.

Docker Compose is encouraged if useful.

Do not introduce unnecessary cloud infrastructure.

---

# 6. Environment Configuration

Use `.env` for secrets. There should be just ONE API key.

Example:

```env
ANTHROPIC_API_KEY=
```

Never commit secrets.

Create:

```text
.env.example
```

with empty values.

---

# 7. Repository Structure

Aim for a structure similar to:

```text
omnipro-agent/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── artifacts/
│   │   ├── hooks/
│   │   ├── lib/
│   │   └── types/
│   ├── package.json
│   └── ...
│
├── backend/
│   ├── agent/
│   │   ├── agent.py
│   │   ├── prompts.py
│   │   └── tools.py
│   │
│   ├── ingestion/
│   │   ├── pdf.py
│   │   ├── images.py
│   │   ├── tables.py
│   │   └── pipeline.py
│   │
│   ├── retrieval/
│   │   ├── semantic.py
│   │   ├── structured.py
│   │   └── reranker.py
│   │
│   ├── artifacts/
│   │   ├── diagrams.py
│   │   ├── calculators.py
│   │   └── flowcharts.py
│   │
│   ├── main.py
│   └── ...
│
├── data/
│   ├── raw/
│   ├── pages/
│   ├── visuals/
│   ├── chunks/
│   └── structured/
│
├── scripts/
│   ├── ingest_manual.py
│   ├── render_pages.py
│   ├── extract_tables.py
│   └── evaluate.py
│
├── tests/
│   ├── test_duty_cycle.py
│   ├── test_polarity.py
│   ├── test_retrieval.py
│   └── test_agent.py
│
├── .env.example
├── .gitignore
├── README.md
└── docker-compose.yml
```

Adapt this structure as implementation progresses.

---

# 8. Phase 1 — Inspect the Existing Repository

Before implementing anything:

1. Inspect the entire repository.
2. Inspect all files in `files/`.
3. Identify all manuals and supporting documents.
4. Determine their file formats.
5. Determine whether any existing code should be reused.
6. Determine available development tooling.
7. Do NOT blindly overwrite existing work.

First produce a concise internal understanding of:

* available documents
* available images
* existing application code
* existing dependencies
* existing frontend/backend structure

Then begin implementation.

---

# 9. Phase 2 — Manual Ingestion Pipeline

The manuals are the primary source of truth.

Do not rely only on ordinary PDF text extraction.

For every manual:

## 9.1 Render every page

Create an image for each page:

```text
data/pages/
  page_001.png
  page_002.png
  ...
```

Preserve page numbers.

## 9.2 Extract text

Extract text while retaining:

* page number
* section
* subsection
* headings
* paragraphs
* lists
* tables where possible

## 9.3 Identify visual content

Index:

* diagrams
* schematics
* charts
* tables
* photographs
* weld examples
* control-panel illustrations
* mechanical illustrations

For each visual, store metadata similar to:

```json
{
  "id": "tig_polarity_diagram",
  "page": 19,
  "type": "diagram",
  "description": "TIG cable/polarity configuration",
  "image_path": "..."
}
```

The exact schema may differ.

---

# 10. Phase 3 — Structured Knowledge Extraction

Do not make the LLM rediscover deterministic facts every time.

Extract important information into structured data.

At minimum, identify and structure:

## Duty cycles

Fields should include:

* process
* input voltage
* amperage
* duty cycle
* source page

Example:

```json
{
  "process": "MIG",
  "input_voltage": 240,
  "amperage": 200,
  "duty_cycle_percent": 20,
  "source_page": 12
}
```

Do NOT assume the numbers above are correct. Extract the actual values from the manual.

## Polarity

Capture:

* process
* torch/electrode connection
* work clamp connection
* polarity
* socket/terminal
* source page

## Troubleshooting

Capture relationships such as:

```text
symptom
→ possible cause
→ recommended action
→ source page
```

## Settings

Where the manual provides them, structure:

* process
* material
* thickness
* wire diameter
* voltage
* wire speed
* polarity
* other relevant settings
* source page

## Error codes

Structure:

```text
error code
→ meaning
→ corrective action
→ source page
```

## Parts

Where useful:

```text
part number
→ name
→ description
→ diagram/page
```

---

# 11. Phase 4 — Knowledge Architecture

Use three complementary knowledge layers.

## Layer 1 — Raw source

Original:

* PDF
* page images
* extracted visual regions

## Layer 2 — Semantic knowledge

Chunks suitable for semantic search.

Example:

```json
{
  "id": "...",
  "page": 19,
  "section": "TIG Welding",
  "content": "...",
  "embedding": "..."
}
```

## Layer 3 — Structured facts

Database records for deterministic information.

Examples:

* duty cycles
* polarity
* settings
* troubleshooting mappings
* error codes

---

# 12. Phase 5 — Hybrid Retrieval

Implement hybrid retrieval.

The agent should have access to both:

### Semantic retrieval

For questions such as:

> "My weld has bubbles and looks porous. What am I doing wrong?"

Search semantically across:

* troubleshooting
* weld diagnosis
* process instructions
* relevant visual content

### Structured retrieval

For questions such as:

> "What is the duty cycle at 200A on 240V?"

Use an exact structured lookup when possible.

Do not ask the LLM to calculate or infer a value that already exists as an exact manual fact.

---

# 13. Claude Agent Tools

Expose useful capabilities to Claude through tools.

At minimum implement:

## `search_manual`

```text
search_manual(query)
```

Returns relevant manual passages with:

* page
* section
* content
* relevance
* source identifier

## `search_visuals`

```text
search_visuals(query)
```

Returns relevant:

* diagrams
* charts
* schematics
* photographs
* manual page images

## `lookup_duty_cycle`

```text
lookup_duty_cycle(
    process,
    input_voltage,
    amperage
)
```

## `lookup_polarity`

```text
lookup_polarity(process)
```

## `troubleshoot`

```text
troubleshoot(
    process,
    symptom,
    context
)
```

## `lookup_settings`

```text
lookup_settings(
    process,
    material,
    thickness,
    wire_diameter
)
```

Only return settings supported by the manual.

## `get_manual_page`

```text
get_manual_page(page_number)
```

Returns the page image and metadata.

---

# 14. Tool Design Principles

Tools should:

1. Return source references.
2. Return page numbers.
3. Return structured information where possible.
4. Never silently invent information.
5. Clearly indicate when no matching information exists.

For example:

```json
{
  "found": false,
  "message": "The manual does not specify a setting for this exact combination."
}
```

is preferable to guessing.

---

# 15. Agent Behavior

The Claude agent should reason about what type of request it received.

Use approximately this decision process:

```text
User question
     ↓
Understand intent
     ↓
Is this a deterministic fact?
     ├── yes → structured lookup
     │
     └── no
          ↓
Does it require manual knowledge?
     ├── yes → retrieve evidence
     │
     └── no → normal reasoning where appropriate
          ↓
Does it involve visual/spatial information?
     ├── yes → retrieve/generate visual
     │
     └── no
          ↓
Does it require troubleshooting?
     ├── yes → diagnostic workflow
     │
     └── no
          ↓
Answer
```

---

# 16. Multimodal Response Policy

This is one of the most important requirements.

The agent should actively choose a visual response when appropriate.

Prefer visual output for:

* polarity
* cable connections
* socket locations
* control-panel instructions
* wiring
* mechanical assembly
* spatial relationships
* complicated troubleshooting
* charts
* settings matrices
* weld diagnosis
* process comparisons

Do NOT simply write:

> "Connect the cable to the negative terminal."

If the user would benefit from seeing the physical connection, show the relevant manual diagram or generate a clear diagram.

---

# 17. Artifact System

Do not allow the model to generate arbitrary frontend code for every answer.

Instead, create a structured artifact protocol.

Example:

```typescript
type Artifact =
  | {
      type: "diagram";
      title: string;
      data: unknown;
    }
  | {
      type: "manual_page";
      page: number;
    }
  | {
      type: "duty_cycle_calculator";
      data: unknown;
    }
  | {
      type: "troubleshooting_flowchart";
      data: unknown;
    }
  | {
      type: "settings_configurator";
      data: unknown;
    };
```

Claude chooses the artifact type and supplies structured data.

React renders the artifact deterministically.

---

# 18. Required Artifact #1 — Polarity Diagram

Build an interactive polarity/cable connection diagram.

For example:

```text
TIG TORCH
    │
    ▼
[ MACHINE SOCKET ]

WORK CLAMP
    │
    ▼
[ MACHINE SOCKET ]
```

The actual connections must come from the manual.

Features:

* clearly labeled cables
* clearly labeled sockets
* polarity
* process
* interactive highlighting
* source page
* link to original manual diagram

Do not hard-code incorrect connection information.

---

# 19. Required Artifact #2 — Duty Cycle Calculator

Create an interactive calculator.

Inputs:

* process
* input voltage
* amperage

Output:

* duty cycle
* relevant explanation
* source page

The result MUST come from structured manual data.

Do not hallucinate values.

If the exact combination is not present:

> "The manual does not provide a duty-cycle value for this exact configuration."

Do not interpolate unless the manual explicitly supports doing so.

---

# 20. Required Artifact #3 — Troubleshooting Flowchart

Build an interactive troubleshooting tree.

Example:

```text
POROSITY
   │
   ├── Material clean?
   │      │
   │      ├── No → Clean material
   │      └── Yes
   │
   ├── Check wire
   │
   ├── Check technique
   │
   └── Check settings
```

Every node should ideally link to:

* explanation
* relevant manual section
* source page
* relevant visual

The tree should be based on manual troubleshooting information.

---

# 21. Required Artifact #4 — Welding Settings Configurator

Build a settings configurator where appropriate.

Inputs may include:

* process
* material
* thickness
* wire diameter
* input voltage

Output:

* recommended settings supported by the manual
* polarity
* wire feed
* voltage
* relevant notes
* source pages

The configurator must be conservative.

If the manual does not contain enough information:

> "I don't have a manual-backed recommendation for this exact combination."

Do not invent settings.

---

# 22. Manual Viewer

Implement a manual viewer.

When a source is cited:

```text
Manual — Page 19
[View Page]
```

Clicking should show the actual page image.

Useful features:

* zoom
* page navigation
* source highlighting if practical
* visual crop if practical

A user should be able to verify important claims against the original source.

---

# 23. Source Cards

Every important technical response should be able to expose evidence.

Example:

```text
┌──────────────────────────────┐
│ SOURCE                       │
│                              │
│ Vulcan OmniPro 220 Manual   │
│ Page 19                      │
│ TIG Welding                  │
│                              │
│ [Open page] [View diagram]   │
└──────────────────────────────┘
```

Do not bury citations in tiny text.

Technical trust should be visible.

---

# 24. Image Upload

Add support for uploading an image of:

* a weld
* machine setup
* control panel
* cable connections
* wire feed mechanism

Claude should be able to inspect the image and then retrieve relevant manual evidence.

Example workflow:

```text
User image
   ↓
Claude vision analysis
   ↓
Identify likely symptom/context
   ↓
Manual retrieval
   ↓
Compare with manual diagnosis
   ↓
Answer + relevant visual + sources
```

Do not claim certainty when an image is ambiguous.

Use language such as:

> "This appears consistent with..."

rather than:

> "This definitely is..."

---

# 25. Clarification Behavior

The agent should ask concise clarifying questions when required.

Bad:

> "Here's everything you need to know about troubleshooting your welder..."

Good:

> "Which welding process are you using: MIG, flux-cored, TIG, or stick?"

Bad:

> "Your welder isn't working. Here's a 20-step troubleshooting guide."

Good:

> "When you pull the trigger, does the machine power on but fail to feed wire, or does nothing happen?"

The agent should minimize unnecessary questioning.

---

# 26. Safety Rules

This is a welding machine.

Add explicit safety constraints to the agent.

The agent must:

1. Never invent machine specifications.
2. Never invent electrical connections.
3. Never invent polarity.
4. Never invent settings.
5. Never fabricate manual citations.
6. Never fabricate page numbers.
7. Distinguish manual instructions from general welding knowledge.
8. Be conservative with electrical and internal-service instructions.
9. Recommend following manufacturer safety procedures.
10. Ask for clarification when the process/configuration is unclear.
11. Surface relevant warnings from the manual when applicable.
12. Avoid presenting uncertain information as fact.

If the manual is authoritative for a machine-specific instruction, prefer the manual.

---

# 27. Hallucination Prevention

Implement an evidence-first response policy.

For machine-specific claims:

```text
Claim
 ↓
Evidence?
 ├── yes → answer + source
 └── no → state uncertainty / ask clarification
```

Never create a plausible-sounding answer merely because one seems likely.

For example:

```text
"I couldn't find a manual-backed value for that exact configuration."
```

is an acceptable answer.

---

# 28. Agent System Prompt Principles

The system prompt should establish that:

* the manual is the primary authority for machine-specific information
* retrieved evidence should be used for technical claims
* sources should be cited
* visual information should be surfaced when useful
* ambiguity should trigger clarification
* unsupported values should never be invented
* the agent should prioritize practical explanations
* the agent should be concise unless complexity requires detail

Do not put the entire manual into the system prompt.

Use tools for retrieval.

---

# 29. Evaluation Dataset

Create a test suite before final polish.

At minimum, create 50 questions covering:

### Simple factual

* duty cycle
* voltage
* amperage
* wire diameter
* process capabilities

### Multi-hop

* process + voltage + polarity
* process + material + settings
* troubleshooting + visual diagnosis

### Visual

* identify diagram
* identify socket
* interpret a chart
* interpret a schematic

### Troubleshooting

* porosity
* poor penetration
* wire feed issues
* arc issues
* overheating
* incorrect polarity

### Ambiguous

* "My welder isn't working."
* "Which setting should I use?"
* "Why is my weld bad?"

### Adversarial

Questions for which the manual does NOT contain enough information.

The agent should explicitly acknowledge missing information.

---

# 30. Evaluation Metrics

Track:

## Accuracy

Is the technical answer correct?

## Source accuracy

Does the cited page actually support the answer?

## Retrieval quality

Did the system retrieve the right manual section?

## Visual relevance

Did it surface the correct diagram/image?

## Hallucination rate

Did it invent unsupported information?

## Clarification quality

Did it ask for the right missing information?

## Artifact correctness

Does the generated calculator/configurator use the correct source data?

---

# 31. Unit Tests

At minimum write tests for:

```text
test_duty_cycle_lookup
test_polarity_lookup
test_manual_search
test_visual_search
test_missing_setting
test_missing_duty_cycle
test_source_page_accuracy
test_troubleshooting
```

Also test malformed inputs.

---

# 32. Integration Tests

Test complete flows:

### Flow 1

```text
User asks duty cycle
→ Agent calls lookup
→ Correct result
→ Source page
→ UI renders calculator
```

### Flow 2

```text
User asks TIG polarity
→ Agent retrieves polarity
→ Retrieves visual
→ UI renders diagram
→ Source page available
```

### Flow 3

```text
User asks troubleshooting question
→ Agent retrieves relevant evidence
→ Generates troubleshooting flow
→ Each step has source
```

### Flow 4

```text
User uploads weld image
→ Vision analysis
→ Manual retrieval
→ Diagnosis
→ Visual evidence
```

---

# 33. UI/UX Priorities

The UI should feel like a modern AI product, not a developer prototype.

Prioritize:

* clean typography
* clear hierarchy
* excellent spacing
* responsive design
* smooth streaming
* clear tool/artifact states
* source cards
* visual artifacts
* loading states
* error states
* empty states
* mobile compatibility where practical

Avoid unnecessary UI complexity.

---

# 34. Chat Experience

Support:

* streaming assistant responses
* markdown
* code-free technical formatting
* source cards
* artifact cards
* image attachments
* manual page previews

Potential quick-start prompts:

```text
How do I set up TIG?
What's the duty cycle at 200A?
Why is my flux-core weld porous?
Which polarity should I use?
Help me configure this welder.
```

---

# 35. Visual Design Principle

The most important design rule:

> If a visual would make the answer easier to understand, show the visual.

Examples:

### Text is enough

> "The machine supports MIG, flux-cored, TIG, and stick."

### Visual is better

> "Connect the TIG torch here and the work clamp here."

### Interactive is better

> "Let's troubleshoot your porosity problem."

### Calculator is better

> "What's my duty cycle?"

Use the right medium for the problem.

---

# 36. Voice — Stretch Goal

Only implement voice after the core system works.

Potential flow:

```text
User speaks
 ↓
Speech-to-text
 ↓
Claude Agent
 ↓
Response
 ↓
Text-to-speech
```

Voice should not compromise the core experience.

---

# 37. Advanced Stretch Goals

If the core product is already excellent, consider:

### Camera mode

Point the camera at the machine.

The assistant identifies:

* front panel
* sockets
* controls
* wire feed assembly

### Visual machine walkthrough

Step-by-step guided setup.

### Persistent session

Remember:

* process
* material
* wire
* machine configuration

### Personalized troubleshooting

```text
User:
I'm welding 1/8" steel with .030 wire.

Assistant:
Got it. I'll use that configuration for the rest
of this troubleshooting session.
```

### Manual image annotation

Highlight the exact component being discussed.

### Parts explorer

Interactive parts diagram.

### "Show me"

Commands such as:

> "Show me where the ground clamp goes."

should immediately produce a visual.

---

# 38. Development Priorities

Work in this order.

## P0 — Required

1. Inspect repository
2. Ingest manuals
3. Render manual pages
4. Extract text
5. Index visuals
6. Structured knowledge extraction
7. Hybrid retrieval
8. Claude Agent SDK integration
9. `search_manual`
10. `search_visuals`
11. `lookup_duty_cycle`
12. `lookup_polarity`
13. `troubleshoot`
14. Source citations
15. Basic chat UI

## P1 — High Value

16. Manual viewer
17. Polarity diagram
18. Duty-cycle calculator
19. Troubleshooting flowchart
20. Settings configurator
21. Evaluation suite
22. Image upload

## P2 — Polish

23. Better visual artifacts
24. Animations
25. Streaming polish
26. Image annotation
27. Improved source UX
28. Responsive design

## P3 — Stretch

29. Voice
30. Camera mode
31. Persistent user configuration
32. Advanced interactive machine walkthrough

Do not start P2/P3 until P0 is reliable.

---

# 39. Important Engineering Constraint

Do not over-engineer the infrastructure.

This is an engineering challenge, not a production SaaS deployment.

Prefer:

```text
FastAPI
+
Postgres/pgvector
+
Claude Agent SDK
+
React
```

over introducing many unnecessary services.

The goal is to demonstrate:

* excellent reasoning
* excellent retrieval
* multimodal understanding
* excellent UX
* strong engineering judgment

---

# 40. Definition of Done

The project is complete when a reviewer can:

### Question 1

Ask:

> "What's the duty cycle for MIG at 200A on 240V?"

and receive:

* correct answer
* manual source
* page
* interactive duty-cycle artifact

### Question 2

Ask:

> "What polarity setup do I need for TIG?"

and receive:

* correct answer
* relevant manual evidence
* visual polarity diagram
* original manual diagram/page

### Question 3

Ask:

> "I'm getting porosity in my flux-cored welds."

and receive:

* useful troubleshooting
* relevant manual evidence
* interactive troubleshooting flow
* relevant weld diagnosis visuals

### Question 4

Upload a weld image and receive:

* visual analysis
* appropriately cautious diagnosis
* relevant manual evidence
* useful next steps

### Question 5

Ask an unsupported question and receive:

* explicit uncertainty
* no fabricated facts
* no fake citations

---

# 41. Final Demo Flow

The final demo should ideally follow this sequence:

## Demo 1 — Factual

> "What's the duty cycle for MIG at 200A on 240V?"

Show:

* answer
* source
* calculator

## Demo 2 — Multimodal

> "How do I set up TIG?"

Show:

* explanation
* interactive polarity diagram
* original manual diagram
* page citation

## Demo 3 — Troubleshooting

> "I'm getting porosity."

Show:

* clarifying question if necessary
* troubleshooting tree
* relevant manual visuals

## Demo 4 — Image understanding

Upload a weld image.

Show:

* visual interpretation
* manual cross-reference
* recommended troubleshooting path

## Demo 5 — Unsupported information

Ask for something the manual does not specify.

Show that the agent refuses to invent an answer.

---

# 42. Coding Agent Instructions

While implementing this project:

### Always

* inspect existing code before modifying it
* keep changes modular
* use typed interfaces
* write tests for critical functionality
* preserve source/page metadata
* make machine-specific claims traceable to evidence
* keep secrets out of source control
* use the Claude Agent SDK as the agent foundation
* prioritize correctness over feature count

### Never

* fabricate manual information
* fabricate citations
* hard-code values without verifying them against the manual
* silently interpolate missing settings
* treat generic welding knowledge as manufacturer-specific instructions
* build only a text chatbot
* sacrifice correctness for a flashy demo
* add unnecessary infrastructure

---

# 43. First Task

Start by inspecting the repository and all files in `files/`.

Do NOT immediately build the frontend.

First:

1. Determine exactly what manuals/documents are available.
2. Determine their formats and page counts.
3. Inspect the existing repository.
4. Identify the critical technical sections.
5. Build the document ingestion/indexing pipeline.
6. Create a structured representation of the manual.
7. Verify the extracted information against the original pages.
8. Build the Claude tools.
9. Implement the evaluation questions.
10. Only then build and polish the frontend.

At the end of each major phase, verify that the implementation actually works before moving on.

The final result should be a **multimodal technical expert for the Vulcan OmniPro 220**, not merely a chatbot with a PDF attached.
