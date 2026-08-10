from api.evidence import build_artifact, extract_evidence, to_media_url


def test_to_media_url_strips_data_prefix():
    assert to_media_url("data/pages/owner-manual/page_024.png") == "/media/pages/owner-manual/page_024.png"


def test_extract_evidence_duty_cycle_found():
    result = {
        "found": True,
        "process": "MIG",
        "input_voltage": 240,
        "amperage": 200,
        "duty_cycle_percent": 25,
        "welding_current_range": "30-220A",
        "source_page": 7,
    }
    evidence = extract_evidence("mcp__omnipro__lookup_duty_cycle", result)
    assert len(evidence) == 1
    assert evidence[0]["type"] == "fact"
    assert evidence[0]["fact_kind"] == "duty_cycle"
    assert evidence[0]["page"] == 7


def test_extract_evidence_duty_cycle_not_found_produces_no_evidence():
    result = {"found": False, "message": "not found", "available_data_points_for_this_process_and_voltage": []}
    evidence = extract_evidence("mcp__omnipro__lookup_duty_cycle", result)
    assert evidence == []


def test_extract_evidence_unknown_tool_returns_empty():
    evidence = extract_evidence("mcp__omnipro__nonexistent_tool", {"found": True})
    assert evidence == []


def test_build_artifact_duty_cycle_includes_all_records(db):
    result = {"found": True, "process": "MIG", "input_voltage": 240, "amperage": 200, "source_page": 7}
    artifact = build_artifact("mcp__omnipro__lookup_duty_cycle", result, db)
    assert artifact["artifact_type"] == "duty_cycle_calculator"
    assert len(artifact["data"]["records"]) == 12
    assert artifact["data"]["highlight"] == {"process": "MIG", "input_voltage": 240, "amperage": 200}


def test_build_artifact_duty_cycle_not_found_still_returns_calculator(db):
    """Even on a miss, the calculator artifact should still appear so the user
    can explore what IS available -- just with no pre-selected highlight."""
    result = {"found": False}
    artifact = build_artifact("mcp__omnipro__lookup_duty_cycle", result, db)
    assert artifact is not None
    assert artifact["data"]["highlight"] is None
    assert len(artifact["data"]["records"]) == 12


def test_build_artifact_troubleshoot_no_matches_returns_none(db):
    result = {"troubleshooting_table_matches": [], "weld_diagnosis_matches": []}
    artifact = build_artifact("mcp__omnipro__troubleshoot", result, db)
    assert artifact is None


def test_build_artifact_unknown_tool_returns_none(db):
    assert build_artifact("mcp__omnipro__search_manual", {"results": []}, db) is None
