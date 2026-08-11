# Vulcan OmniPro 220 — AI Welding Assistant

A multimodal technical support agent for the Vulcan OmniPro 220 welding machine, built on the Claude Agent SDK. It answers deep technical questions grounded in the actual owner's manual, surfaces the right diagram instead of describing it in prose, and generates interactive artifacts (a duty-cycle calculator, a polarity diagram, a troubleshooting flowchart, a settings explorer) backed by real extracted manual data — never invented numbers. Upload a photo of your own machine and it draws numbered markers directly on it instead of describing locations in words; voice input and read-aloud both work through the browser, no extra API key required.

<img src="product.webp" alt="Vulcan OmniPro 220" width="360" />

🎥 [Watch the video walkthrough](https://drive.google.com/file/d/1uYSZKHNJ7L11SZNHdXhkhTurXD-gCB_J/view?usp=sharing)

**Live demo:** https://omnipro-385920925770.us-central1.run.app (no signup, no API key needed on your end — go ask it something)

The live demo uses my personal API key, and my current resources for API costs may be limited. An alternative is to follow the quickstart section to clone the repo and run it locally.

---

## Quick start

```bash
git clone https://github.com/sprihaapandey/prox-challenge.git
cd prox-challenge
cp .env.example .env
# edit .env and set ANTHROPIC_API_KEY

# 1. Postgres + pgvector
docker compose up -d postgres

# 2. Backend (needs Python 3.12+; claude-agent-sdk requires it)
cd backend
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
npm install          
cd ..

# 3. Load the pre-extracted knowledge base into Postgres (fast, local, no extra API cost, < 1 min>)
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
     │ annotate_image (marks up a user-uploaded photo)  │
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
   Streamed text response  +  a persistent side panel (desktop) that
   independently renders source citations and the interactive artifact
   (calculator/diagram/flowchart/configurator/annotated photo) as soon as
   each is ready — never buried by or burying the other — plus an in-app
   Manual Viewer (zoom, page nav)
```

### The three knowledge layers

1. **Raw source** (`data/pages/*.png`) — every PDF page rendered to an image at 2x scale. This is the ground truth a user can always fall back to verify a claim against, via the in-app Manual Viewer.
2. **Semantic knowledge** (`data/chunks/*.json`, `data/visuals/*.json` → Postgres `chunks`/`visuals` tables) — page text split into clean two-column-aware chunks, and a Claude-vision-generated catalog of every diagram/chart/photo per page. Both are embedded locally (`sentence-transformers/all-MiniLM-L6-v2`) for pgvector cosine similarity search.
3. **Structured facts** (`data/structured/*.json` → Postgres `duty_cycle`/`polarity`/`troubleshooting`/`weld_diagnosis`/`parts` tables) — deterministic records for duty cycle, polarity/socket assignments, troubleshooting tables, weld-diagnosis cards, and the parts list. Tools query these directly for exact answers instead of asking the LLM to re-derive a fact from prose every time.

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
| `annotate_image` | Places numbered, labeled markers on a user-uploaded photo (coordinates read off a grid overlay) — how the agent points at *your* welder, not the manual's |

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
  components/     chat UI, evidence/source cards, manual viewer modal,
                  VisualsPanel (the persistent side-panel workspace)
  components/artifacts/  the 5 interactive artifact renderers
  context/        manual viewer state
  hooks/useChat.ts             SSE client + message state machine
  hooks/useSpeechRecognition.ts, useSpeechSynthesis.ts   voice in/out

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
- **Auto-crop of individual diagrams was deliberately dropped** in favor of always-correct full-page images with a best-effort highlight overlay.
- **No live camera mode** — photo upload + annotation is implemented (see `annotate_image` above); pointing a live camera feed at the machine for real-time analysis was out of scope given the time budget.
- **No access control on the live demo** — it was deliberately removed (see git history) in favor of zero-friction access for reviewers; every chat turn spends real Anthropic API credit, so this is a known, accepted tradeoff for a temporary demo link rather than a production posture.
