"""Identify and catalog visual content (diagrams, schematics, charts, photos) per page.

This runs offline during ingestion, so it talks to the Messages API directly
rather than through the runtime agent. Claude vision looks at the full
rendered page and reports back a structured list of distinct visual regions
via forced tool-use (guarantees parseable JSON, no prompt-fencing needed).

Manual pages here pack several labeled diagrams closely together with shared
callouts, and vision-model bounding-box regression is not reliable enough to
crop them apart without clipping labels (verified empirically — even with a
percentage-grid overlay as a reading aid, crops routinely cut off legends).
So the canonical visual asset for every catalogued entry is always the full
page image; `highlight_bbox_pct` is kept only as a best-effort hint a
frontend can use to draw a soft highlight box over the full page, which
degrades gracefully when imprecise (unlike a hard crop).
"""

from __future__ import annotations

import asyncio
import base64
from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path
from typing import Any

from anthropic import AsyncAnthropic
from PIL import Image, ImageDraw

VISION_MODEL = "claude-sonnet-4-5-20250929"
MAX_CONCURRENCY = 6
GRID_STEP_PCT = 10
GRID_COLOR = (255, 0, 0)

RECORD_VISUALS_TOOL = {
    "name": "record_visuals",
    "description": "Record the distinct visual elements found on this manual page.",
    "input_schema": {
        "type": "object",
        "properties": {
            "page_summary": {
                "type": "string",
                "description": "One sentence describing the visual content of this page as a whole, for search purposes. Empty string if the page is plain body text with no meaningful visuals.",
            },
            "visuals": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "description": "short snake_case slug unique within the page, e.g. 'tig_dcen_polarity_diagram'",
                        },
                        "type": {
                            "type": "string",
                            "enum": ["diagram", "schematic", "chart", "photo", "table", "illustration"],
                        },
                        "title": {"type": "string"},
                        "description": {
                            "type": "string",
                            "description": "1-3 sentences on what it shows and what technical information it conveys.",
                        },
                        "bbox_pct": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 4,
                            "maxItems": 4,
                            "description": "[x0, y0, x1, y1] approximate bounding box as a percentage (0-100) of page width/height. Best-effort only, used for a soft on-page highlight, not a hard crop.",
                        },
                    },
                    "required": ["id", "type", "title", "description", "bbox_pct"],
                },
            },
        },
        "required": ["page_summary", "visuals"],
    },
}

SYSTEM_PROMPT = """You are indexing a welding machine owner's manual page-by-page so a support \
agent can later surface the right diagram/photo/chart for a user's question. \
Identify every DISTINCT visual element that is not just a paragraph of body text: \
diagrams (e.g. cable/socket connections, assembly steps), schematics, photographs, \
charts (e.g. duty cycle dials), tables rendered as a boxed graphic, and illustrations. \
Do not report plain paragraphs or bullet lists of text as visuals. \
Do not report the page's decorative sidebar tab strip as a visual.

The image has a red reference grid overlaid, with lines every 10% of width/height, \
labeled with their percentage value along the top and left edges. Use these gridlines \
to estimate bbox_pct for each visual. The grid is only a reading aid; describe the \
underlying diagram/photo, not the grid itself."""


def _with_grid_overlay(image: Image.Image) -> Image.Image:
    gridded = image.convert("RGB").copy()
    draw = ImageDraw.Draw(gridded)
    w, h = gridded.size
    for pct in range(0, 101, GRID_STEP_PCT):
        x = int(w * pct / 100)
        y = int(h * pct / 100)
        draw.line([(x, 0), (x, h)], fill=GRID_COLOR, width=1)
        draw.line([(0, y), (w, y)], fill=GRID_COLOR, width=1)
        draw.text((x + 2, 2), str(pct), fill=GRID_COLOR)
        draw.text((2, y + 2), str(pct), fill=GRID_COLOR)
    return gridded


def _encode_png(image: Image.Image) -> str:
    buf = BytesIO()
    image.save(buf, format="PNG")
    return base64.standard_b64encode(buf.getvalue()).decode("utf-8")


@dataclass
class VisualEntry:
    id: str
    type: str
    title: str
    description: str
    doc_id: str
    page_number: int
    image_path: str  # always the full page image; see module docstring
    highlight_bbox_pct: list[float]


@dataclass
class PageVisualResult:
    page_number: int
    page_summary: str
    visuals: list[VisualEntry] = field(default_factory=list)


async def analyze_page(
    client: AsyncAnthropic,
    doc_id: str,
    page_number: int,
    page_image_path: Path,
) -> PageVisualResult:
    page_image = Image.open(page_image_path)
    gridded = _with_grid_overlay(page_image)
    b64 = _encode_png(gridded)
    response = await client.messages.create(
        model=VISION_MODEL,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        tools=[RECORD_VISUALS_TOOL],
        tool_choice={"type": "tool", "name": "record_visuals"},
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": "image/png", "data": b64},
                    },
                    {
                        "type": "text",
                        "text": f"This is page {page_number} of the manual. Identify its visual elements.",
                    },
                ],
            }
        ],
    )

    tool_use = next(b for b in response.content if b.type == "tool_use")
    data: dict[str, Any] = tool_use.input

    entries = [
        VisualEntry(
            id=v["id"],
            type=v["type"],
            title=v["title"],
            description=v["description"],
            doc_id=doc_id,
            page_number=page_number,
            image_path=str(page_image_path),
            highlight_bbox_pct=v["bbox_pct"],
        )
        for v in data.get("visuals", [])
    ]

    return PageVisualResult(page_number=page_number, page_summary=data.get("page_summary", ""), visuals=entries)


async def analyze_document(
    doc_id: str,
    page_image_paths: list[tuple[int, Path]],
    api_key: str,
) -> list[PageVisualResult]:
    client = AsyncAnthropic(api_key=api_key)
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

    async def _bounded(page_number: int, path: Path) -> PageVisualResult:
        async with semaphore:
            return await analyze_page(client, doc_id, page_number, path)

    results = await asyncio.gather(*[_bounded(pn, p) for pn, p in page_image_paths])
    return sorted(results, key=lambda r: r.page_number)
