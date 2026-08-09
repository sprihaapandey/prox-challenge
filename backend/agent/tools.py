"""Claude Agent SDK tools: the agent's only way to touch the knowledge base.

Every tool returns JSON in its text content block. Structured lookups
(duty cycle, polarity, settings, parts) hit Layer 3 tables for an exact,
deterministic answer and explicitly say found=false rather than guess.
search_manual/search_visuals hit Layer 2 embeddings for fuzzy/exploratory
questions. troubleshoot combines an exact keyword match with a semantic
fallback across both troubleshooting tables and weld-diagnosis cards.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import asdict
from typing import Any

from claude_agent_sdk import create_sdk_mcp_server, tool

from db.session import new_session
from retrieval import semantic, structured


def _json_result(data: Any) -> dict:
    return {"content": [{"type": "text", "text": json.dumps(data, indent=2)}]}


async def _run(fn, *args):
    """Run a blocking DB call off the event loop."""
    return await asyncio.to_thread(fn, *args)


# ---------------------------------------------------------------------------


def _search_manual(session, query: str, doc_id: str | None):
    results = semantic.search_chunks(session, query, doc_id=doc_id)
    return [
        {
            "doc_id": r.doc_id,
            "page": r.page,
            "section": r.section,
            "content": r.content,
            "relevance": round(r.relevance, 3),
        }
        for r in results
    ]


@tool(
    "search_manual",
    "Semantic search over the manual's text content. Use for open-ended or exploratory questions "
    "(e.g. 'how do I load a wire spool', 'what does CTWD mean') where you need relevant passages "
    "rather than one exact fact. Returns passages with page, section, content, and relevance.",
    {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "natural-language search query"},
            "doc_id": {
                "type": "string",
                "enum": ["owner-manual", "quick-start-guide", "selection-chart"],
                "description": "restrict to one document; omit to search all manuals",
            },
        },
        "required": ["query"],
    },
)
async def search_manual(args: dict) -> dict:
    session = new_session()
    try:
        results = await _run(_search_manual, session, args["query"], args.get("doc_id"))
    finally:
        session.close()
    return _json_result({"results": results})


def _search_visuals(session, query: str, doc_id: str | None):
    results = semantic.search_visuals(session, query, doc_id=doc_id)
    return [
        {
            "id": r.id,
            "doc_id": r.doc_id,
            "page": r.page,
            "type": r.type,
            "title": r.title,
            "description": r.description,
            "image_path": r.image_path,
            "relevance": round(r.relevance, 3),
        }
        for r in results
    ]


@tool(
    "search_visuals",
    "Semantic search over the manual's catalogued diagrams, schematics, charts, and photos. Use "
    "whenever the user's question involves cable/socket connections, spatial layout, control-panel "
    "buttons, wiring, mechanical assembly, or anything easier to show than describe. Returns the "
    "matching visual's page image (image_path) so it can be displayed to the user.",
    {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "natural-language description of the visual you need"},
            "doc_id": {
                "type": "string",
                "enum": ["owner-manual", "quick-start-guide", "selection-chart"],
            },
        },
        "required": ["query"],
    },
)
async def search_visuals_tool(args: dict) -> dict:
    session = new_session()
    try:
        results = await _run(_search_visuals, session, args["query"], args.get("doc_id"))
    finally:
        session.close()
    return _json_result({"results": results})


@tool(
    "lookup_duty_cycle",
    "Exact structured lookup of duty cycle from the Specifications table. Do not compute or guess "
    "duty cycle yourself — always call this. Returns found=false (with the nearby data points that "
    "DO exist) if the exact process/voltage/amperage combination isn't in the manual.",
    {
        "type": "object",
        "properties": {
            "process": {"type": "string", "enum": ["MIG", "Flux-Cored", "TIG", "Stick"]},
            "input_voltage": {"type": "integer", "enum": [120, 240]},
            "amperage": {"type": "integer"},
        },
        "required": ["process", "input_voltage", "amperage"],
    },
)
async def lookup_duty_cycle(args: dict) -> dict:
    session = new_session()
    try:
        result = await _run(
            structured.lookup_duty_cycle, session, args["process"], args["input_voltage"], args["amperage"]
        )
    finally:
        session.close()
    return _json_result(result)


@tool(
    "lookup_polarity",
    "Exact structured lookup of the cable-to-socket polarity setup for a welding process "
    "(which socket the ground clamp and gun/torch/electrode cable each plug into, and why). "
    "Always call this instead of recalling polarity from memory — it differs by process on this machine.",
    {
        "type": "object",
        "properties": {"process": {"type": "string", "enum": ["MIG", "Flux-Cored", "TIG", "Stick"]}},
        "required": ["process"],
    },
)
async def lookup_polarity(args: dict) -> dict:
    session = new_session()
    try:
        result = await _run(structured.lookup_polarity, session, args["process"])
    finally:
        session.close()
    return _json_result(result)


@tool(
    "lookup_settings",
    "Look up what the manual documents about settings/capabilities for a process (wire/rod/electrode "
    "diameter options, gas requirements and flow rate, polarity). IMPORTANT: this machine uses an "
    "auto-set synergic LCD control, so the manual does NOT print a numeric 'material+thickness -> "
    "voltage+wire speed' table — this tool's result will make that explicit. Never invent specific "
    "voltage/WFS numbers for a material+thickness combination yourself.",
    {
        "type": "object",
        "properties": {"process": {"type": "string", "enum": ["MIG", "Flux-Cored", "TIG", "Stick"]}},
        "required": ["process"],
    },
)
async def lookup_settings(args: dict) -> dict:
    result = await _run(structured.lookup_settings, args["process"])
    return _json_result(result)


def _troubleshoot(session, process: str | None, symptom: str, context: str | None):
    exact_table = structured.troubleshoot_exact(session, process, symptom)
    exact_diagnosis = structured.weld_diagnosis_exact(session, process, symptom)

    if exact_table or exact_diagnosis:
        return {
            "match_type": "exact",
            "troubleshooting_table_matches": [
                {
                    "process": t.process,
                    "symptom": t.symptom,
                    "possible_causes": t.possible_causes,
                    "recommended_actions": t.recommended_actions,
                    "source_pages": t.source_pages,
                }
                for t in exact_table
            ],
            "weld_diagnosis_matches": [
                {
                    "process": w.process,
                    "defect_name": w.defect_name,
                    "visual_description": w.visual_description,
                    "possible_causes_and_solutions": w.possible_causes_and_solutions,
                    "source_page": w.source_page,
                }
                for w in exact_diagnosis
            ],
        }

    query = f"{symptom}. {context or ''}".strip()
    table_hits = semantic.search_troubleshooting_semantic(session, query, limit=3)
    diagnosis_hits = semantic.search_weld_diagnosis_semantic(session, query, limit=3)
    return {
        "match_type": "semantic",
        "message": "No exact symptom match; showing closest matches by meaning.",
        "troubleshooting_table_matches": [
            {
                "process": t.process,
                "symptom": t.symptom,
                "possible_causes": t.possible_causes,
                "recommended_actions": t.recommended_actions,
                "source_pages": t.source_pages,
                "relevance": round(rel, 3),
            }
            for t, rel in table_hits
        ],
        "weld_diagnosis_matches": [
            {
                "process": w.process,
                "defect_name": w.defect_name,
                "visual_description": w.visual_description,
                "possible_causes_and_solutions": w.possible_causes_and_solutions,
                "source_page": w.source_page,
                "relevance": round(rel, 3),
            }
            for w, rel in diagnosis_hits
        ],
    }


@tool(
    "troubleshoot",
    "Look up manual-backed troubleshooting guidance for a symptom (e.g. 'porosity', 'wire not "
    "feeding', 'welder won't turn on'). Tries an exact match against the manual's Problem/Cause/"
    "Solution tables and weld-diagnosis cards first, falling back to semantic search over the same "
    "data if nothing matches exactly. If the symptom is vague (e.g. just 'welder isn't working'), "
    "ask the user a clarifying question before calling this rather than guessing a symptom keyword.",
    {
        "type": "object",
        "properties": {
            "process": {
                "type": "string",
                "enum": ["MIG", "Flux-Cored", "TIG", "Stick"],
                "description": "omit if unknown or not process-specific",
            },
            "symptom": {"type": "string", "description": "short symptom keyword/phrase, e.g. 'porosity'"},
            "context": {"type": "string", "description": "any additional detail the user gave, to improve semantic matching"},
        },
        "required": ["symptom"],
    },
)
async def troubleshoot(args: dict) -> dict:
    session = new_session()
    try:
        result = await _run(_troubleshoot, session, args.get("process"), args["symptom"], args.get("context"))
    finally:
        session.close()
    return _json_result(result)


@tool(
    "lookup_part",
    "Look up a part by number or by name/description keyword from the Parts List (e.g. 'grounding "
    "clamp assembly', or part number 30). Returns description, quantity, and the parts-diagram page.",
    {
        "type": "object",
        "properties": {"query": {"type": "string", "description": "part number or name/description keyword"}},
        "required": ["query"],
    },
)
async def lookup_part(args: dict) -> dict:
    session = new_session()
    try:
        parts = await _run(structured.lookup_part, session, args["query"])
    finally:
        session.close()
    if not parts:
        return _json_result({"found": False, "message": f"No part matched '{args['query']}'."})
    return _json_result(
        {
            "found": True,
            "parts": [
                {
                    "part_number": p.part_number,
                    "description": p.description,
                    "qty": p.qty,
                    "source_page": p.source_page,
                    "diagram_page": p.diagram_page,
                }
                for p in parts
            ],
        }
    )


@tool(
    "get_manual_page",
    "Fetch a specific manual page's image and metadata by page number, so the user can view/verify "
    "the original source. Use this to back up a claim with 'View page N' or when the user asks to "
    "see a page directly.",
    {
        "type": "object",
        "properties": {
            "page_number": {"type": "integer"},
            "doc_id": {
                "type": "string",
                "enum": ["owner-manual", "quick-start-guide", "selection-chart"],
                "description": "defaults to owner-manual",
            },
        },
        "required": ["page_number"],
    },
)
async def get_manual_page(args: dict) -> dict:
    doc_id = args.get("doc_id", "owner-manual")
    result = await _run(structured.get_manual_page_metadata, doc_id, args["page_number"])
    if result is None:
        return _json_result({"found": False, "message": f"No page {args['page_number']} in {doc_id}."})
    return _json_result({"found": True, **result})


ALL_TOOLS = [
    search_manual,
    search_visuals_tool,
    lookup_duty_cycle,
    lookup_polarity,
    lookup_settings,
    troubleshoot,
    lookup_part,
    get_manual_page,
]

TOOL_NAMES = [f"mcp__omnipro__{t.name}" for t in ALL_TOOLS]


def build_mcp_server():
    return create_sdk_mcp_server(name="omnipro", version="0.1.0", tools=ALL_TOOLS)
