# Vulcan OmniPro 220 — AI Welding Assistant

A multimodal technical support agent for the Vulcan OmniPro 220 welding machine, built on the Claude Agent SDK. It answers deep technical questions grounded in the actual owner's manual, surfaces the right diagram instead of describing it in prose, and generates interactive artifacts (a duty-cycle calculator, a polarity diagram, a troubleshooting checklist, a settings explorer) backed by real extracted manual data — never invented numbers.

<img src="product.webp" alt="Vulcan OmniPro 220" width="360" />

The original challenge brief is preserved in [CHALLENGE.md](CHALLENGE.md).

---

## Quick start

```bash
git clone <your-fork>
cd prox-challenge
cp .env.example .env
# edit .env and set ANTHROPIC_API_KEY

# 1. Postgres + pgvector
docker compose up -d postgres

# 2. Backend (needs Python 3.12+; claude-agent-sdk requires it)
cd backend
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
npm install          # installs the Claude Code CLI the Agent SDK drives — see "Why a CLI dependency?" below
cd ..

# 3. Load the pre-extracted knowledge base into Postgres (fast, local, no extra API cost)
backend/.venv/bin/python scripts/load_knowledge_base.py

# 4. Start the backend
backend/.venv/bin/uvicorn backend.main:app --app-dir . --port 8000

# 5. In a second terminal — frontend
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**.

The manual has already been fully ingested and extracted — `data/chunks/`, `data/structured/`, `data/visuals/`, and `data/pages/` (the rendered page images the UI serves) are all committed to the repo. Step 3 just loads that pre-built knowledge into Postgres with local embeddings computed on the fly; it does **not** re-run the (much slower, API-cost-incurring) ingestion pipeline. See [Reproducing ingestion from scratch](#reproducing-ingestion-from-scratch) if you want to regenerate it.

---

## Architecture

```
User
  │
  ▼
React chat UI  ──(SSE)──►  FastAPI /api/chat
                                  │
                                  ▼
                    Claude Agent SDK session
                    (persistent per conversation)
                                  │
                                  ▼
                          Tool selection
     ┌────────────────────────────────────────────────┐
     │ search_manual        search_visuals             │
     │ lookup_duty_cycle    lookup_polarity             │
     │ lookup_settings      troubleshoot                │
     │ lookup_part          get_manual_page             │
     └────────────────────────────────────────────────┘
                                  │
        ┌─────────────────────────┴─────────────────────────┐
        ▼                         ▼                          ▼
  Layer 3: structured       Layer 2: semantic           Layer 1: raw
  facts (Postgres)          chunks/visuals              pages (PNG,
  exact, deterministic      (pgvector cosine             served as
  lookups                   search)                      static files)
        │                         │                          │
        └─────────────────────────┴──────────────────────────┘
                                  │
                                  ▼
                  Evidence + Artifacts (derived from
                  the same tool results, not a
                  separate "generate artifact" tool)
                                  │
                                  ▼
        Streamed response + Source citations + Interactive
        artifact (calculator/diagram/flowchart/configurator)
        + in-app Manual Viewer (zoom, page nav)
```

### The three knowledge layers

1. **Raw source** (`data/pages/*.png`) — every PDF page rendered to an image at 2x scale. This is the ground truth a user can always fall back to verify a claim against, via the in-app Manual Viewer.
2. **Semantic knowledge** (`data/chunks/*.json`, `data/visuals/*.json` → Postgres `chunks`/`visuals` tables) — page text split into clean two-column-aware chunks, and a Claude-vision-generated catalog of every diagram/chart/photo per page. Both are embedded locally (`sentence-transformers/all-MiniLM-L6-v2`) for pgvector cosine similarity search.
3. **Structured facts** (`data/structured/*.json` → Postgres `duty_cycle`/`polarity`/`troubleshooting`/`weld_diagnosis`/`parts` tables) — deterministic records for duty cycle, polarity/socket assignments, troubleshooting tables, weld-diagnosis cards, and the parts list. Tools query these directly for exact answers instead of asking the LLM to re-derive a fact from prose every time.

---

## Key design decisions

**The Claude Agent SDK is literally the Claude Code CLI, and that has real consequences.** `claude-agent-sdk` drives the same CLI binary that powers Claude Code, as a subprocess. Tested unrestricted, it pulled the full coding-agent tool surface (Bash, Edit, Write, memory paths, skills, sub-agents) into a customer-facing welding assistant, cost roughly 10x more per turn (~$0.09 vs ~$0.01 for a comparable direct API call), and added a hidden secondary model call I couldn't fully suppress. Fixed by setting `tools=[]` and `setting_sources=[]` (strips it to just the 8 domain tools registered via an in-process MCP server) and using `ClaudeSDKClient` for a **persistent session per conversation** rather than the one-shot `query()` helper, so the CLI subprocess is spawned once per conversation instead of once per turn.

**No separate "generate artifact" tool.** An artifact (duty-cycle calculator, polarity diagram, troubleshooting checklist, settings explorer) is deterministically derived server-side from the same fact-lookup tool call the agent already had to make to answer the question (see `backend/api/evidence.py::build_artifact`). This guarantees every artifact is backed by a real, necessary tool call — the model can't forget to "generate" one, and it can't show one backed by invented data.

**Full manual pages, not auto-cropped diagrams.** I tried having Claude vision return bounding boxes to crop individual diagrams out of each page — even with a percentage-grid overlay as a grounding aid, the crops were unreliable enough to clip labels off diagrams, and once returned wildly out-of-range coordinates. Rather than ship inconsistent crops, every catalogued visual points at its full (always-correct) page image; the bounding box is kept only as a soft, validated highlight hint in the Manual Viewer that degrades gracefully to "no highlight" if the coordinates look implausible.

**Two "the manual doesn't have this" findings are baked into the data, not guessed at query time.** (1) This machine uses a synergic auto-set LCD — there is no printed "material + thickness → voltage + wire speed" table, confirmed by inspecting the relevant pages directly. (2) There's no discrete error-code table (no "E1"/"Er-2" style codes anywhere in 48 pages — confirmed by grep across the full extracted text), only two generic LCD warning conditions. Both are recorded explicitly in `data/structured/settings.json` and `error_codes.json` with source pages, so the agent states the real behavior instead of inventing numbers or a fake code table.

**Structured extraction was hand-verified against page images, not blindly LLM-scanned.** For each category (duty cycle, polarity, troubleshooting, weld diagnosis, parts), I first visually inspected the actual rendered page to identify the correct source page(s) and expected values, *then* ran targeted Claude-vision extraction against those specific pages with forced JSON schemas, and cross-checked the output against what I'd already read by eye. `tests/test_source_page_accuracy.py` encodes those verified page numbers as a regression test.

**Local embeddings.** Anthropic has no first-party embeddings endpoint, and the brief requires the whole app to run on one `ANTHROPIC_API_KEY`. `sentence-transformers` runs entirely on-device, so semantic search doesn't need a second API key or external service.

**Citations render after the response finishes, not mid-stream.** Evidence/source cards originally appeared the instant each tool call resolved, which felt noisy while the model was still composing its answer. They now render as a "Sources" section once streaming completes, alongside a lightweight live status pill ("Checking duty cycle chart…") during generation.

**Polarity genuinely differs by process** — this directly answers the brief's example question ("which socket does the ground clamp go in?"). Ground clamp: **Negative** for MIG, **Positive** for Flux-Cored, **Positive** for TIG, **Negative** for Stick. Each verified against its own cable-connection diagram page (14, 13, 24, 27 respectively) — see `tests/test_polarity.py`.

### Why a CLI dependency in a Python backend?

`claude-agent-sdk` requires the Claude Code CLI on disk; `npm install` in `backend/` installs it as a local (not global) dependency so it stays scoped to this project rather than requiring a global install.

---

## Agent tools

| Tool | Purpose |
|---|---|
| `search_manual` | Semantic search over manual text for open-ended questions |
| `search_visuals` | Semantic search over the catalogued diagram/chart/photo index |
| `lookup_duty_cycle` | Exact `(process, voltage, amperage) → duty cycle %` lookup; `found: false` + nearby data points if no exact match |
| `lookup_polarity` | Exact cable→socket polarity lookup per process |
| `lookup_settings` | What the manual documents about a process's capabilities (wire/gas/polarity) — makes explicit that no numeric settings table exists |
| `troubleshoot` | Exact symptom match against the Problem/Cause/Solution tables and weld-diagnosis cards, semantic fallback if nothing matches exactly |
| `lookup_part` | Part number or description → parts-list entry |
| `get_manual_page` | Fetch a specific page's image + metadata to back up a citation |

Safety and hallucination-prevention rules (never invent a spec/connection/polarity/setting, distinguish manual fact from general welding knowledge, cite real page numbers only, stay hedged on image analysis, defer to a qualified technician for internal repairs) are encoded in `backend/agent/prompts.py`.

---

## Testing

```bash
# Unit tests (fast, free — direct DB queries, no LLM calls): 50 tests
backend/.venv/bin/python -m pytest tests/ --ignore=tests/eval -v

# Integration tests (real API calls, ~$0.20 total, ~2 min): the plan's 4 required
# flows (duty cycle, TIG polarity, troubleshooting, image upload) plus adversarial
# and clarification flows
backend/.venv/bin/python -m pytest tests/test_agent_integration.py -v -m integration

# Full evaluation suite: 52 questions across simple-factual / multi-hop / visual /
# troubleshooting / ambiguous / adversarial categories (tests/eval/dataset.py),
# with automated checks where reliable and full transcripts saved for the rest
backend/.venv/bin/python scripts/evaluate.py
```

`tests/test_source_page_accuracy.py` is worth calling out specifically: it pins every structured fact's cited page number against the values I hand-verified by viewing the actual rendered manual pages, so a future re-extraction that silently drifts gets caught.

---

## Deploying

One container serves both the API and the built frontend as static files (`backend/Dockerfile` builds the frontend, then bundles it with the Python+Node backend — the Agent SDK's CLI subprocess needs Node either way, see above), plus a separate Postgres container:

```bash
cp .env.example .env   # set ANTHROPIC_API_KEY; optionally CORS_ORIGINS (below)
docker compose -f docker-compose.prod.yml up -d --build

# first deploy only — load the pre-extracted knowledge base into the fresh prod DB
docker compose -f docker-compose.prod.yml exec app python scripts/load_knowledge_base.py
```

Verified working end-to-end this way (build, container start, health check, frontend serving, and a real chat round-trip) before writing this down.

**`CORS_ORIGINS`**: comma-separated extra allowed origins, needed if the frontend is ever served from a different origin than the API (not the case with the one-container setup above, but kept configurable).

`docker-compose.prod.yml` declares its own Compose project name (`omnipro-prod`) specifically so it can never collide with the local dev stack's `docker-compose.yml` — both define a service literally named `postgres`, and without separate project names Compose treats them as the same service slot and recreates whichever container is running under the shared default project name (the directory name). Learned this from a real recreate event while validating the prod file locally; the named volume survived so no data was lost, but it's a sharp edge worth avoiding.

---

## Reproducing ingestion from scratch

Not needed to run the app (see Quick start), but if you want to regenerate `data/` from the source PDFs in `files/`:

```bash
backend/.venv/bin/python scripts/ingest_manual.py        # render pages, extract text, catalog visuals (Claude vision — costs API calls, ~5-10 min)
backend/.venv/bin/python scripts/extract_structured.py    # duty cycle / polarity / troubleshooting / weld diagnosis / parts
backend/.venv/bin/python scripts/load_knowledge_base.py   # load everything into Postgres
```

---

## Project structure

```
backend/
  agent/          agent.py (persistent Claude Agent SDK session), tools.py, prompts.py
  api/            evidence.py — normalizes tool results into evidence + artifacts for the frontend
  db/             SQLAlchemy models, session, local embeddings
  ingestion/      PDF rendering, text extraction, vision-based visual cataloging, structured extraction
  retrieval/      semantic.py (pgvector search), structured.py (exact lookups)
  main.py         FastAPI app — SSE chat endpoint, upload, static media

frontend/src/
  components/     chat UI, evidence/source cards, manual viewer modal
  components/artifacts/  the 4 interactive artifact renderers
  context/        manual viewer state
  hooks/useChat.ts        SSE client + message state machine

data/
  pages/          rendered manual page images (served at /media/pages/...)
  chunks/         semantic text chunks (pre-embedding)
  visuals/        visual catalog (pre-embedding)
  structured/     duty cycle, polarity, troubleshooting, weld diagnosis, parts, settings, error codes

scripts/          ingest_manual.py, extract_structured.py, load_knowledge_base.py, evaluate.py
tests/            unit tests, integration tests, eval dataset + results
```

---

## Known limitations

- **Per-turn latency (~5-25s)** is dominated by the Claude Agent SDK's CLI subprocess overhead, not model inference — a direct Messages API tool-use loop would be faster and cheaper, but the brief specifically requires the Claude Agent SDK. The persistent-session fix keeps this to one-time-per-conversation rather than one-time-per-turn.
- **Auto-crop of individual diagrams was deliberately dropped** (see above) in favor of always-correct full-page images with a best-effort highlight overlay.
- **No voice / camera mode** — out of scope given the time budget; the plan explicitly treats these as stretch goals after the core product is solid.
