from retrieval.semantic import search_troubleshooting_semantic, search_weld_diagnosis_semantic
from retrieval.structured import troubleshoot_exact, weld_diagnosis_exact


def test_troubleshoot_exact_symptom_match(db):
    results = troubleshoot_exact(db, "MIG", "Porosity")
    assert len(results) == 1
    entry = results[0]
    assert entry.process == "MIG / Flux-Cored"
    assert len(entry.possible_causes) == len(entry.recommended_actions)
    assert 42 in entry.source_pages or 43 in entry.source_pages


def test_troubleshoot_exact_process_scoping(db):
    """'Porosity' as a table symptom only exists in the MIG/Flux-Cored table,
    not the TIG/Stick table -- scoping to TIG should find nothing."""
    results = troubleshoot_exact(db, "TIG", "Porosity in the Weld Metal")
    assert results == []


def test_troubleshoot_semantic_fallback_finds_something_for_vague_symptom(db):
    results = search_troubleshooting_semantic(db, "welder won't turn on at all", limit=3)
    assert len(results) > 0
    top_entry, relevance = results[0]
    assert relevance > 0


def test_weld_diagnosis_exact_match(db):
    results = weld_diagnosis_exact(db, "Stick", "Porosity")
    assert len(results) == 1
    assert results[0].source_page == 40


def test_weld_diagnosis_semantic_search_bubbles_query(db):
    """The exact defect name in the manual is 'Porosity', not 'bubbles' --
    semantic search should still connect a layperson's phrasing to it."""
    results = search_weld_diagnosis_semantic(db, "my weld has bubbles in it", limit=3)
    defect_names = [w.defect_name.lower() for w, _ in results]
    assert any("poros" in name for name in defect_names)


def test_troubleshoot_malformed_empty_symptom_does_not_crash(db):
    results = troubleshoot_exact(db, None, "")
    assert isinstance(results, list)
