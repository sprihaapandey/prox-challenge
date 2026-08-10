"""Every structured fact must cite a page that actually supports it. These
bounds were established by manually viewing the rendered page images during
Phase 3 -- see backend/ingestion/structured_extract.py's per-category
comments for exactly which pages were inspected."""

from db.models import DutyCycle, Part, Polarity, TroubleshootingEntry, WeldDiagnosis


def test_duty_cycle_source_pages_all_page_7(db):
    rows = db.query(DutyCycle).all()
    assert len(rows) == 12
    assert all(r.source_page == 7 for r in rows)


def test_polarity_source_pages_match_known_diagrams(db):
    expected_pages = {"MIG": 14, "Flux-Cored": 13, "TIG": 24, "Stick": 27}
    rows = db.query(Polarity).all()
    assert len(rows) == 4
    for r in rows:
        assert r.source_page == expected_pages[r.process]


def test_troubleshooting_source_pages_in_expected_range(db):
    rows = db.query(TroubleshootingEntry).all()
    assert len(rows) == 13
    for r in rows:
        assert set(r.source_pages).issubset({42, 43, 44})


def test_weld_diagnosis_source_pages_in_expected_range(db):
    rows = db.query(WeldDiagnosis).all()
    assert len(rows) == 18
    for r in rows:
        assert r.source_page in (37, 38, 39, 40)


def test_parts_source_page_and_diagram_page(db):
    rows = db.query(Part).all()
    assert len(rows) == 61
    assert all(r.source_page == 46 and r.diagram_page == 47 for r in rows)
    assert {r.part_number for r in rows} == set(range(1, 62))
