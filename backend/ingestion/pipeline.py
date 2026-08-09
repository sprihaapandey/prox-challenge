"""Orchestrates the full ingestion pipeline for one manual PDF:

render pages -> extract text (Layer 1 + inputs to Layer 2) -> index visuals

Writes:
  data/pages/{doc_id}/page_NNN.png
  data/chunks/{doc_id}.json    (semantic chunks: one per page, with section)
  data/visuals/{doc_id}.json   (visual catalog: one entry per identified diagram/photo/chart)
"""

from __future__ import annotations

import asyncio
import dataclasses
import json
import os
from pathlib import Path

from .render import render_document
from .text_extract import extract_document_text
from .visuals import analyze_document

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = REPO_ROOT / "data"


@dataclasses.dataclass
class IngestResult:
    doc_id: str
    num_pages: int
    num_chunks: int
    num_visuals: int


def ingest_document(doc_id: str, pdf_path: Path, api_key: str) -> IngestResult:
    pages_dir = DATA_DIR / "pages" / doc_id
    print(f"[{doc_id}] rendering pages -> {pages_dir}")
    rendered = render_document(pdf_path, pages_dir)

    print(f"[{doc_id}] extracting text + sections")
    doc_text = extract_document_text(pdf_path, doc_id)

    chunks = [
        {
            "id": f"{doc_id}_p{p.page_number:03d}",
            "doc_id": doc_id,
            "page": p.page_number,
            "section": p.section,
            "content": p.text,
        }
        for p in doc_text.pages
        if p.text.strip()
    ]
    chunks_path = DATA_DIR / "chunks" / f"{doc_id}.json"
    chunks_path.parent.mkdir(parents=True, exist_ok=True)
    chunks_path.write_text(json.dumps(chunks, indent=2))
    print(f"[{doc_id}] wrote {len(chunks)} text chunks -> {chunks_path}")

    print(f"[{doc_id}] indexing visuals via Claude vision ({len(rendered)} pages)")
    page_paths = [(rp.page_number, rp.image_path) for rp in rendered]
    visual_results = asyncio.run(analyze_document(doc_id, page_paths, api_key))

    visuals = []
    for r in visual_results:
        for v in r.visuals:
            rel_path = str(Path(v.image_path).relative_to(REPO_ROOT))
            visuals.append(
                {
                    "id": f"{doc_id}_p{v.page_number:03d}_{v.id}",
                    "doc_id": v.doc_id,
                    "page": v.page_number,
                    "type": v.type,
                    "title": v.title,
                    "description": v.description,
                    "image_path": rel_path,
                    "highlight_bbox_pct": v.highlight_bbox_pct,
                }
            )
    page_summaries = {r.page_number: r.page_summary for r in visual_results if r.page_summary}

    visuals_path = DATA_DIR / "visuals" / f"{doc_id}.json"
    visuals_path.parent.mkdir(parents=True, exist_ok=True)
    visuals_path.write_text(json.dumps({"visuals": visuals, "page_summaries": page_summaries}, indent=2))
    print(f"[{doc_id}] wrote {len(visuals)} visual entries -> {visuals_path}")

    return IngestResult(
        doc_id=doc_id,
        num_pages=len(rendered),
        num_chunks=len(chunks),
        num_visuals=len(visuals),
    )


def ingest_all(documents: dict[str, Path]) -> list[IngestResult]:
    api_key = os.environ["ANTHROPIC_API_KEY"]
    results = []
    for doc_id, pdf_path in documents.items():
        results.append(ingest_document(doc_id, pdf_path, api_key))
    return results
