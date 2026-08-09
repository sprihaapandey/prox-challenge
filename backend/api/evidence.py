"""Normalizes each tool's raw JSON result into a uniform evidence item the
frontend can render as a source card / image, without needing to know every
tool's individual schema. Phase 8's artifact system builds on top of this.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


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
