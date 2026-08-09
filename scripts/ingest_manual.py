#!/usr/bin/env python3
"""Run the ingestion pipeline over every manual in files/.

Usage (from repo root, using the backend venv):
    backend/.venv/bin/python scripts/ingest_manual.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "backend"))

from dotenv import load_dotenv

load_dotenv(REPO_ROOT / ".env")

from ingestion.pipeline import ingest_all  # noqa: E402

DOCUMENTS = {
    "owner-manual": REPO_ROOT / "files" / "owner-manual.pdf",
    "quick-start-guide": REPO_ROOT / "files" / "quick-start-guide.pdf",
    "selection-chart": REPO_ROOT / "files" / "selection-chart.pdf",
}


def main() -> None:
    results = ingest_all(DOCUMENTS)
    print("\n=== Ingestion summary ===")
    for r in results:
        print(f"{r.doc_id}: {r.num_pages} pages, {r.num_chunks} chunks, {r.num_visuals} visuals")


if __name__ == "__main__":
    main()
