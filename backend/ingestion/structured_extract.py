"""Extract deterministic structured facts from specific, manually-verified manual pages.

Unlike the page-by-page visual catalog in visuals.py, this module targets exact
pages identified by inspecting the manual directly (see comments per category),
because these are the facts tools will return verbatim to users (duty cycle,
polarity/socket assignments, troubleshooting steps) — they must be exactly
right, not merely "probably in this general area."

Every record carries a source_page so the agent can cite it and a user can
verify it against the original manual page.
"""

from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any

from anthropic import Anthropic

MODEL = "claude-sonnet-4-5-20250929"


def _b64(path: Path) -> str:
    return base64.standard_b64encode(path.read_bytes()).decode("utf-8")


def _image_block(path: Path) -> dict:
    return {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": _b64(path)}}


def _extract(
    client: Anthropic,
    pages_dir: Path,
    page_numbers: list[int],
    system_prompt: str,
    tool: dict,
    user_text: str,
) -> Any:
    content = [_image_block(pages_dir / f"page_{n:03d}.png") for n in page_numbers]
    content.append({"type": "text", "text": user_text})
    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=system_prompt,
        tools=[tool],
        tool_choice={"type": "tool", "name": tool["name"]},
        messages=[{"role": "user", "content": content}],
    )
    tool_use = next(b for b in response.content if b.type == "tool_use")
    return tool_use.input


# ---------------------------------------------------------------------------
# Duty cycle — page 7 (Specifications table: MIG/TIG/Stick x 120VAC/240VAC)
# ---------------------------------------------------------------------------

DUTY_CYCLE_TOOL = {
    "name": "record_duty_cycles",
    "description": "Record every duty cycle data point from the Specifications table.",
    "input_schema": {
        "type": "object",
        "properties": {
            "records": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "process": {"type": "string", "enum": ["MIG", "TIG", "Stick"]},
                        "input_voltage": {"type": "integer", "description": "120 or 240"},
                        "amperage": {"type": "integer"},
                        "duty_cycle_percent": {"type": "integer"},
                        "welding_current_range": {
                            "type": "string",
                            "description": "e.g. '30-220A', the full rated range for this process/voltage",
                        },
                    },
                    "required": ["process", "input_voltage", "amperage", "duty_cycle_percent", "welding_current_range"],
                },
            }
        },
        "required": ["records"],
    },
}

DUTY_CYCLE_SYSTEM = """Read the Specifications table on this manual page exactly as printed. \
For each process (MIG, TIG, Stick) and each input voltage (120VAC, 240VAC), the "Rated Duty \
Cycles" cell has two data points, e.g. "40% @ 100A" and "100% @ 75A" — record both as separate \
entries. Also record the "Welding Current Range" for that process/voltage. Transcribe numbers \
exactly; do not compute, round, or infer anything not printed."""


def extract_duty_cycle(client: Anthropic, pages_dir: Path) -> list[dict]:
    data = _extract(
        client,
        pages_dir,
        [7],
        DUTY_CYCLE_SYSTEM,
        DUTY_CYCLE_TOOL,
        "Extract every duty cycle data point from this Specifications page.",
    )
    return [{**r, "source_page": 7} for r in data["records"]]


# ---------------------------------------------------------------------------
# Polarity — one page per process, each with an explicit cable->socket diagram
# ---------------------------------------------------------------------------

POLARITY_PAGES = {
    "MIG": 14,  # DCEP, solid core, gas shielded
    "Flux-Cored": 13,  # DCEN, gasless
    "TIG": 24,  # DC TIG
    "Stick": 27,
}

POLARITY_TOOL = {
    "name": "record_polarity",
    "description": "Record the exact cable-to-socket polarity setup shown on this page.",
    "input_schema": {
        "type": "object",
        "properties": {
            "process": {"type": "string"},
            "polarity_name": {
                "type": "string",
                "description": "e.g. 'DCEP' or 'DCEN' exactly as labeled on the page, or empty string if not named",
            },
            "polarity_full_name": {"type": "string", "description": "e.g. 'Direct Current Electrode Positive'"},
            "gun_or_torch_or_electrode_cable": {
                "type": "string",
                "description": "name of the cable coming from the gun/torch/electrode holder, e.g. 'Wire Feed Power Cable', 'TIG Torch Cable', 'Electrode Holder Cable'",
            },
            "gun_or_torch_or_electrode_socket": {"type": "string", "enum": ["Positive", "Negative"]},
            "ground_clamp_socket": {"type": "string", "enum": ["Positive", "Negative"]},
            "applies_to": {
                "type": "string",
                "description": "one sentence on when this setup applies, e.g. 'Solid core wire welding with shielding gas'",
            },
        },
        "required": [
            "process",
            "polarity_name",
            "gun_or_torch_or_electrode_cable",
            "gun_or_torch_or_electrode_socket",
            "ground_clamp_socket",
            "applies_to",
        ],
    },
}

POLARITY_SYSTEM = """Read the cable connection diagram on this manual page exactly as shown. \
Identify which socket (Positive or Negative) the ground clamp cable plugs into, and which \
socket the gun/torch/electrode cable plugs into. Use only what is explicitly labeled in the \
diagram and instructions — do not infer a polarity that isn't shown on this specific page."""


def extract_polarity(client: Anthropic, pages_dir: Path) -> list[dict]:
    records = []
    for process, page in POLARITY_PAGES.items():
        data = _extract(
            client,
            pages_dir,
            [page],
            POLARITY_SYSTEM,
            POLARITY_TOOL,
            f"Extract the polarity/cable-socket setup for {process} shown on this page.",
        )
        data["process"] = process  # authoritative label; don't trust the model's free-text echo
        data["source_page"] = page
        records.append(data)
    return records


# ---------------------------------------------------------------------------
# Troubleshooting tables — Problem / Possible Causes / Likely Solutions
# ---------------------------------------------------------------------------

TROUBLESHOOT_TOOL = {
    "name": "record_troubleshooting",
    "description": "Record every problem/cause/solution row from this troubleshooting table.",
    "input_schema": {
        "type": "object",
        "properties": {
            "entries": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "symptom": {"type": "string", "description": "the Problem, verbatim"},
                        "possible_causes": {"type": "array", "items": {"type": "string"}},
                        "recommended_actions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "same order/count as possible_causes, each is the fix for the corresponding cause",
                        },
                    },
                    "required": ["symptom", "possible_causes", "recommended_actions"],
                },
            }
        },
        "required": ["entries"],
    },
}

TROUBLESHOOT_SYSTEM = """Read the Problem / Possible Causes / Likely Solutions table on these \
manual pages exactly as printed. The table may span multiple page images provided — treat them \
as one continuous table. For each Problem row, list every numbered cause and its matching \
numbered solution, preserving the numbering/order so cause[i] maps to action[i]. Transcribe text \
verbatim; do not paraphrase or add causes that aren't printed."""

TROUBLESHOOT_TABLES = {
    "MIG / Flux-Cored": [42, 43],
    "TIG / Stick": [44],
}


def extract_troubleshooting(client: Anthropic, pages_dir: Path) -> list[dict]:
    records = []
    for process, pages in TROUBLESHOOT_TABLES.items():
        data = _extract(
            client,
            pages_dir,
            pages,
            TROUBLESHOOT_SYSTEM,
            TROUBLESHOOT_TOOL,
            f"Extract the full {process} troubleshooting table from these pages.",
        )
        for entry in data["entries"]:
            records.append(
                {
                    "process": process,
                    "symptom": entry["symptom"],
                    "possible_causes": entry["possible_causes"],
                    "recommended_actions": entry["recommended_actions"],
                    "source_pages": pages,
                }
            )
    return records


# ---------------------------------------------------------------------------
# Weld diagnosis — visual symptom cards (appearance -> cause -> fix)
# ---------------------------------------------------------------------------

WELD_DIAGNOSIS_TOOL = {
    "name": "record_weld_diagnosis",
    "description": "Record every weld-appearance diagnosis card on this page.",
    "input_schema": {
        "type": "object",
        "properties": {
            "entries": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "defect_name": {"type": "string", "description": "e.g. 'Porosity', 'Burn-Through'"},
                        "visual_description": {
                            "type": "string",
                            "description": "how the defect looks, as described/captioned on the page",
                        },
                        "possible_causes_and_solutions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "cause": {"type": "string"},
                                    "solution": {"type": "string"},
                                },
                                "required": ["cause", "solution"],
                            },
                        },
                    },
                    "required": ["defect_name", "visual_description", "possible_causes_and_solutions"],
                },
            }
        },
        "required": ["entries"],
    },
}

WELD_DIAGNOSIS_SYSTEM = """Read the weld-diagnosis cards on this manual page (each shows a weld \
defect name, a picture/description of its appearance, and numbered causes with matching \
solutions). Transcribe each card's defect name, appearance description, and every numbered \
cause+solution pair verbatim."""

WELD_DIAGNOSIS_PAGES = {
    "MIG / Flux-Cored": [37],
    "Stick": [38, 39, 40],
}


def extract_weld_diagnosis(client: Anthropic, pages_dir: Path) -> list[dict]:
    records = []
    for process, pages in WELD_DIAGNOSIS_PAGES.items():
        for page in pages:
            data = _extract(
                client,
                pages_dir,
                [page],
                WELD_DIAGNOSIS_SYSTEM,
                WELD_DIAGNOSIS_TOOL,
                f"Extract the {process} weld diagnosis cards on this page.",
            )
            for entry in data["entries"]:
                records.append({"process": process, "source_page": page, **entry})
    return records


# ---------------------------------------------------------------------------
# Parts list — page 46 is a clean two-column "Part | Description | Qty" table,
# already reliably captured by plain text extraction; no vision call needed.
# ---------------------------------------------------------------------------


def extract_parts(chunks_path: Path) -> list[dict]:
    chunks = json.loads(chunks_path.read_text())
    page_46 = next(c for c in chunks if c["page"] == 46)
    records = []
    for line in page_46["content"].split("\n"):
        parts = line.strip().rsplit(" ", 1)
        if len(parts) != 2 or not parts[1].isdigit():
            continue
        left, qty = parts
        left_parts = left.split(" ", 1)
        if len(left_parts) != 2 or not left_parts[0].isdigit():
            continue
        part_number, description = left_parts
        records.append(
            {
                "part_number": int(part_number),
                "description": description.strip(),
                "qty": int(qty),
                "source_page": 46,
                "diagram_page": 47,
            }
        )
    # dedupe/sort defensively in case any stray numeric line slipped through
    seen = {}
    for r in records:
        seen[r["part_number"]] = r
    return [seen[k] for k in sorted(seen)]
