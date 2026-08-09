"""Exact, deterministic lookups over Layer 3 (structured facts).

These never guess: an exact match returns the manual-backed value with its
source page; no match returns found=False with the nearby options that DO
exist, rather than interpolating or inventing a number.
"""

from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from db.models import DutyCycle, Part, Polarity, TroubleshootingEntry, WeldDiagnosis

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
STRUCTURED_DIR = REPO_ROOT / "data" / "structured"

_PROCESS_ALIASES = {
    "mig": "MIG",
    "gmaw": "MIG",
    "solid core": "MIG",
    "solid-core": "MIG",
    "flux cored": "Flux-Cored",
    "flux-cored": "Flux-Cored",
    "fluxcore": "Flux-Cored",
    "flux core": "Flux-Cored",
    "fcaw": "Flux-Cored",
    "tig": "TIG",
    "gtaw": "TIG",
    "stick": "Stick",
    "smaw": "Stick",
}


def normalize_process(process: str) -> str:
    return _PROCESS_ALIASES.get(process.strip().lower(), process.strip())


def lookup_duty_cycle(session: Session, process: str, input_voltage: int, amperage: int) -> dict:
    proc = normalize_process(process)
    # Duty cycle is only tabulated for MIG and Stick (Flux-Cored shares MIG's power-source spec;
    # the manual doesn't print a separate Flux-Cored row).
    lookup_proc = "MIG" if proc == "Flux-Cored" else proc

    exact = (
        session.query(DutyCycle)
        .filter(DutyCycle.process == lookup_proc, DutyCycle.input_voltage == input_voltage, DutyCycle.amperage == amperage)
        .first()
    )
    if exact:
        note = None
        if proc == "Flux-Cored":
            note = (
                "The manual's Specifications table lists duty cycle under 'MIG' only; "
                "Flux-Cored shares the same power-source rating (they differ in wire, gas, and polarity, not output current handling)."
            )
        return {
            "found": True,
            "process": proc,
            "input_voltage": exact.input_voltage,
            "amperage": exact.amperage,
            "duty_cycle_percent": exact.duty_cycle_percent,
            "welding_current_range": exact.welding_current_range,
            "source_page": exact.source_page,
            "note": note,
        }

    available = (
        session.query(DutyCycle)
        .filter(DutyCycle.process == lookup_proc, DutyCycle.input_voltage == input_voltage)
        .order_by(DutyCycle.amperage)
        .all()
    )
    return {
        "found": False,
        "message": (
            f"The manual does not provide a duty-cycle value for {proc} at exactly {amperage}A on {input_voltage}V."
        ),
        "available_data_points_for_this_process_and_voltage": [
            {"amperage": d.amperage, "duty_cycle_percent": d.duty_cycle_percent, "source_page": d.source_page}
            for d in available
        ],
    }


def lookup_polarity(session: Session, process: str) -> dict:
    proc = normalize_process(process)
    record = session.query(Polarity).filter(Polarity.process == proc).first()
    if not record:
        all_processes = [p.process for p in session.query(Polarity.process).distinct()]
        return {
            "found": False,
            "message": f"No polarity setup found for process '{process}'.",
            "known_processes": all_processes,
        }
    return {
        "found": True,
        "process": record.process,
        "polarity_name": record.polarity_name,
        "polarity_full_name": record.polarity_full_name,
        "gun_or_torch_or_electrode_cable": record.gun_or_torch_or_electrode_cable,
        "gun_or_torch_or_electrode_socket": record.gun_or_torch_or_electrode_socket,
        "ground_clamp_socket": record.ground_clamp_socket,
        "applies_to": record.applies_to,
        "source_page": record.source_page,
    }


def lookup_settings(process: str) -> dict:
    proc = normalize_process(process)
    data = json.loads((STRUCTURED_DIR / "settings.json").read_text())
    match = next((c for c in data["capabilities"] if c["process"] == proc), None)
    if not match:
        return {
            "found": False,
            "message": f"No settings information found for process '{process}'.",
            "known_processes": [c["process"] for c in data["capabilities"]],
        }
    return {
        "found": True,
        "capability": match,
        "important_caveat": data["note"],
    }


def troubleshoot_exact(session: Session, process: str | None, symptom_keyword: str) -> list[TroubleshootingEntry]:
    """Try a direct symptom substring match within a process's table before falling back to semantic search."""
    q = session.query(TroubleshootingEntry)
    if process:
        proc = normalize_process(process)
        table_process = "MIG / Flux-Cored" if proc in ("MIG", "Flux-Cored") else "TIG / Stick"
        q = q.filter(TroubleshootingEntry.process == table_process)
    return q.filter(TroubleshootingEntry.symptom.ilike(f"%{symptom_keyword}%")).all()


def weld_diagnosis_exact(session: Session, process: str | None, defect_keyword: str) -> list[WeldDiagnosis]:
    q = session.query(WeldDiagnosis)
    if process:
        proc = normalize_process(process)
        table_process = "Stick" if proc == "Stick" else "MIG / Flux-Cored"
        q = q.filter(WeldDiagnosis.process == table_process)
    return q.filter(WeldDiagnosis.defect_name.ilike(f"%{defect_keyword}%")).all()


def lookup_part(session: Session, query: str) -> list[Part]:
    if query.strip().isdigit():
        part = session.query(Part).filter(Part.part_number == int(query.strip())).first()
        return [part] if part else []
    return session.query(Part).filter(Part.description.ilike(f"%{query}%")).all()


def get_manual_page_metadata(doc_id: str, page_number: int) -> dict | None:
    pages_dir = REPO_ROOT / "data" / "pages" / doc_id
    image_path = pages_dir / f"page_{page_number:03d}.png"
    if not image_path.exists():
        return None

    chunks_path = REPO_ROOT / "data" / "chunks" / f"{doc_id}.json"
    section = None
    if chunks_path.exists():
        chunks = json.loads(chunks_path.read_text())
        match = next((c for c in chunks if c["page"] == page_number), None)
        if match:
            section = match["section"]

    visuals_path = REPO_ROOT / "data" / "visuals" / f"{doc_id}.json"
    visuals = []
    if visuals_path.exists():
        vdata = json.loads(visuals_path.read_text())
        visuals = [v for v in vdata["visuals"] if v["page"] == page_number]

    return {
        "doc_id": doc_id,
        "page": page_number,
        "section": section,
        "image_path": str(image_path.relative_to(REPO_ROOT)),
        "visuals_on_page": [{"id": v["id"], "type": v["type"], "title": v["title"]} for v in visuals],
    }
