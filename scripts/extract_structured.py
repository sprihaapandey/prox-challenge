#!/usr/bin/env python3
"""Extract structured facts (duty cycle, polarity, troubleshooting, weld diagnosis,
parts) from the owner manual into data/structured/*.json.

Usage: backend/.venv/bin/python scripts/extract_structured.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "backend"))

from dotenv import load_dotenv

load_dotenv(REPO_ROOT / ".env")

from anthropic import Anthropic  # noqa: E402

from ingestion.structured_extract import (  # noqa: E402
    extract_duty_cycle,
    extract_parts,
    extract_polarity,
    extract_troubleshooting,
    extract_weld_diagnosis,
)

PAGES_DIR = REPO_ROOT / "data" / "pages" / "owner-manual"
CHUNKS_PATH = REPO_ROOT / "data" / "chunks" / "owner-manual.json"
OUT_DIR = REPO_ROOT / "data" / "structured"


def write(name: str, data) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"{name}.json"
    path.write_text(json.dumps(data, indent=2))
    print(f"wrote {len(data)} records -> {path}")


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    write("duty_cycle", extract_duty_cycle(client, PAGES_DIR))
    write("polarity", extract_polarity(client, PAGES_DIR))
    write("troubleshooting", extract_troubleshooting(client, PAGES_DIR))
    write("weld_diagnosis", extract_weld_diagnosis(client, PAGES_DIR))
    write("parts", extract_parts(CHUNKS_PATH))


if __name__ == "__main__":
    main()
