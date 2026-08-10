"""Normalizes each tool's raw JSON result into a uniform evidence item the
frontend can render as a source card / image, without needing to know every
tool's individual schema.

build_artifact() goes a step further for the four fact-lookup tools: rather
than adding separate "generate an artifact" tools the model has to remember
to call, an artifact is deterministically derived from the same lookup the
model already had to make to answer the question. This guarantees every
artifact is backed by a real tool call (never invented) and doesn't add
extra round trips.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from db.models import DutyCycle, Polarity

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
STRUCTURED_DIR = REPO_ROOT / "data" / "structured"


def to_media_url(repo_relative_path: str) -> str:
    """'data/pages/owner-manual/page_024.png' -> '/media/pages/owner-manual/page_024.png'"""
    p = repo_relative_path.replace("\\", "/")
    if p.startswith("data/"):
        p = p[len("data/") :]
    return f"/media/{p}"


def extract_evidence(tool_name: str, result: dict[str, Any]) -> list[dict[str, Any]]:
    name = tool_name.rsplit("__", 1)[-1]
    items: list[dict[str, Any]] = []

    if name == "search_manual":
        for r in result.get("results", []):
            items.append(
                {
                    "type": "page_reference",
                    "doc_id": r["doc_id"],
                    "page": r["page"],
                    "section": r.get("section"),
                    "snippet": r["content"][:240],
                    "relevance": r.get("relevance"),
                }
            )

    elif name == "search_visuals":
        for r in result.get("results", []):
            items.append(
                {
                    "type": "visual",
                    "id": r["id"],
                    "doc_id": r["doc_id"],
                    "page": r["page"],
                    "visual_type": r["type"],
                    "title": r["title"],
                    "description": r["description"],
                    "image_url": to_media_url(r["image_path"]),
                    "highlight_bbox_pct": r.get("highlight_bbox_pct"),
                    "relevance": r.get("relevance"),
                }
            )

    elif name == "get_manual_page" and result.get("found"):
        items.append(
            {
                "type": "page_image",
                "doc_id": result["doc_id"],
                "page": result["page"],
                "section": result.get("section"),
                "image_url": to_media_url(result["image_path"]),
            }
        )

    elif name == "lookup_duty_cycle" and result.get("found"):
        items.append(
            {
                "type": "fact",
                "fact_kind": "duty_cycle",
                "doc_id": "owner-manual",
                "page": result["source_page"],
                "data": result,
            }
        )

    elif name == "lookup_polarity" and result.get("found"):
        items.append(
            {
                "type": "fact",
                "fact_kind": "polarity",
                "doc_id": "owner-manual",
                "page": result["source_page"],
                "data": result,
            }
        )

    elif name == "lookup_settings" and result.get("found"):
        cap = result["capability"]
        items.append(
            {
                "type": "fact",
                "fact_kind": "settings",
                "doc_id": "owner-manual",
                "page": cap.get("source_page"),
                "data": result,
            }
        )

    elif name == "lookup_part" and result.get("found"):
        for p in result.get("parts", []):
            items.append(
                {
                    "type": "fact",
                    "fact_kind": "part",
                    "doc_id": "owner-manual",
                    "page": p["source_page"],
                    "data": p,
                }
            )

    elif name == "troubleshoot":
        for t in result.get("troubleshooting_table_matches", []):
            for page in t.get("source_pages", []):
                items.append(
                    {
                        "type": "page_reference",
                        "doc_id": "owner-manual",
                        "page": page,
                        "section": None,
                        "snippet": t["symptom"],
                        "relevance": t.get("relevance"),
                    }
                )
        for w in result.get("weld_diagnosis_matches", []):
            items.append(
                {
                    "type": "page_reference",
                    "doc_id": "owner-manual",
                    "page": w["source_page"],
                    "section": None,
                    "snippet": w["defect_name"],
                    "relevance": w.get("relevance"),
                }
            )

    return items


def _duty_cycle_row(d: DutyCycle) -> dict[str, Any]:
    return {
        "process": d.process,
        "input_voltage": d.input_voltage,
        "amperage": d.amperage,
        "duty_cycle_percent": d.duty_cycle_percent,
        "welding_current_range": d.welding_current_range,
        "source_page": d.source_page,
    }


def _polarity_row(p: Polarity) -> dict[str, Any]:
    return {
        "process": p.process,
        "polarity_name": p.polarity_name,
        "polarity_full_name": p.polarity_full_name,
        "gun_or_torch_or_electrode_cable": p.gun_or_torch_or_electrode_cable,
        "gun_or_torch_or_electrode_socket": p.gun_or_torch_or_electrode_socket,
        "ground_clamp_socket": p.ground_clamp_socket,
        "applies_to": p.applies_to,
        "source_page": p.source_page,
    }


def build_artifact(tool_name: str, result: dict[str, Any], session: Session) -> dict[str, Any] | None:
    """Returns a full artifact payload for the frontend's deterministic renderers,
    or None if this tool call doesn't warrant one (e.g. a found=false lookup)."""
    name = tool_name.rsplit("__", 1)[-1]

    if name == "lookup_duty_cycle":
        rows = session.query(DutyCycle).order_by(DutyCycle.process, DutyCycle.input_voltage, DutyCycle.amperage).all()
        return {
            "artifact_type": "duty_cycle_calculator",
            "title": "Duty Cycle Calculator",
            "data": {
                "records": [_duty_cycle_row(d) for d in rows],
                "highlight": (
                    {"process": result["process"], "input_voltage": result["input_voltage"], "amperage": result["amperage"]}
                    if result.get("found")
                    else None
                ),
            },
        }

    if name == "lookup_polarity":
        rows = session.query(Polarity).order_by(Polarity.process).all()
        return {
            "artifact_type": "polarity_diagram",
            "title": "Polarity & Cable Connections",
            "data": {
                "records": [_polarity_row(p) for p in rows],
                "highlight": result.get("process") if result.get("found") else None,
            },
        }

    if name == "lookup_settings":
        settings_data = json.loads((STRUCTURED_DIR / "settings.json").read_text())
        return {
            "artifact_type": "settings_configurator",
            "title": "Settings Configurator",
            "data": {
                "capabilities": settings_data["capabilities"],
                "important_caveat": settings_data["note"],
                "highlight": result.get("capability", {}).get("process") if result.get("found") else None,
            },
        }

    if name == "troubleshoot":
        table_matches = result.get("troubleshooting_table_matches", [])
        diagnosis_matches = result.get("weld_diagnosis_matches", [])
        if not table_matches and not diagnosis_matches:
            return None
        return {
            "artifact_type": "troubleshooting_flowchart",
            "title": "Troubleshooting Guide",
            "data": {
                "match_type": result.get("match_type"),
                "table_matches": table_matches,
                "diagnosis_matches": diagnosis_matches,
            },
        }

    return None
