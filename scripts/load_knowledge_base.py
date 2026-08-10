#!/usr/bin/env python3
"""Load data/chunks, data/visuals, and data/structured into Postgres+pgvector.

Computes embeddings locally (sentence-transformers) for every semantically
searchable table. Safe to re-run: drops and recreates all tables each time,
since everything here is derived from files/ and can be regenerated.

Usage: backend/.venv/bin/python scripts/load_knowledge_base.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "backend"))

from dotenv import load_dotenv

load_dotenv(REPO_ROOT / ".env")

from sqlalchemy import text  # noqa: E402

from db.embeddings import embed_texts  # noqa: E402
from db.models import (  # noqa: E402
    Base,
    Chunk,
    DutyCycle,
    Part,
    Polarity,
    TroubleshootingEntry,
    Visual,
    WeldDiagnosis,
)
from db.session import get_engine, new_session  # noqa: E402

CHUNKS_DIR = REPO_ROOT / "data" / "chunks"
VISUALS_DIR = REPO_ROOT / "data" / "visuals"
STRUCTURED_DIR = REPO_ROOT / "data" / "structured"

DOCS = ["owner-manual", "quick-start-guide", "selection-chart"]


def load_chunks(session) -> int:
    count = 0
    for doc_id in DOCS:
        path = CHUNKS_DIR / f"{doc_id}.json"
        if not path.exists():
            continue
        chunks = json.loads(path.read_text())
        if not chunks:
            continue
        texts = [f"{c['section'] or ''}\n{c['content']}".strip() for c in chunks]
        vectors = embed_texts(texts)
        for c, vec in zip(chunks, vectors):
            session.add(
                Chunk(
                    id=c["id"],
                    doc_id=c["doc_id"],
                    page=c["page"],
                    section=c["section"],
                    content=c["content"],
                    embedding=vec,
                )
            )
            count += 1
    return count


def load_visuals(session) -> int:
    count = 0
    for doc_id in DOCS:
        path = VISUALS_DIR / f"{doc_id}.json"
        if not path.exists():
            continue
        data = json.loads(path.read_text())
        visuals = data["visuals"]
        if not visuals:
            continue
        texts = [f"{v['title']}. {v['description']}" for v in visuals]
        vectors = embed_texts(texts)
        for v, vec in zip(visuals, vectors):
            session.add(
                Visual(
                    id=v["id"],
                    doc_id=v["doc_id"],
                    page=v["page"],
                    type=v["type"],
                    title=v["title"],
                    description=v["description"],
                    image_path=v["image_path"],
                    highlight_bbox_pct=v["highlight_bbox_pct"],
                    embedding=vec,
                )
            )
            count += 1
    return count


def load_duty_cycle(session) -> int:
    records = json.loads((STRUCTURED_DIR / "duty_cycle.json").read_text())
    for r in records:
        session.add(DutyCycle(**r))
    return len(records)


def load_polarity(session) -> int:
    records = json.loads((STRUCTURED_DIR / "polarity.json").read_text())
    for r in records:
        session.add(Polarity(**r))
    return len(records)


def load_troubleshooting(session) -> int:
    records = json.loads((STRUCTURED_DIR / "troubleshooting.json").read_text())
    if not records:
        return 0
    texts = [f"{r['symptom']}. " + " ".join(r["possible_causes"]) for r in records]
    vectors = embed_texts(texts)
    for r, vec in zip(records, vectors):
        session.add(TroubleshootingEntry(**r, embedding=vec))
    return len(records)


def load_weld_diagnosis(session) -> int:
    records = json.loads((STRUCTURED_DIR / "weld_diagnosis.json").read_text())
    if not records:
        return 0
    texts = [f"{r['defect_name']}. {r['visual_description']}" for r in records]
    vectors = embed_texts(texts)
    for r, vec in zip(records, vectors):
        session.add(WeldDiagnosis(**r, embedding=vec))
    return len(records)


def load_parts(session) -> int:
    records = json.loads((STRUCTURED_DIR / "parts.json").read_text())
    for r in records:
        session.add(Part(**r))
    return len(records)


def main() -> None:
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    print("Dropping and recreating tables...")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    session = new_session()
    try:
        counts = {
            "chunks": load_chunks(session),
            "visuals": load_visuals(session),
            "duty_cycle": load_duty_cycle(session),
            "polarity": load_polarity(session),
            "troubleshooting": load_troubleshooting(session),
            "weld_diagnosis": load_weld_diagnosis(session),
            "parts": load_parts(session),
        }
        session.commit()
    finally:
        session.close()

    print("\n=== Load summary ===")
    for table, n in counts.items():
        print(f"{table}: {n} rows")


if __name__ == "__main__":
    main()
