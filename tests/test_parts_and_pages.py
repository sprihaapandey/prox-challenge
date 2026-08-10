from retrieval.structured import get_manual_page_metadata, lookup_part


def test_lookup_part_by_number(db):
    parts = lookup_part(db, "30")
    assert len(parts) == 1
    assert parts[0].description == "Grounding Clamp Assembly"


def test_lookup_part_by_description_keyword(db):
    parts = lookup_part(db, "grounding clamp")
    assert len(parts) == 1
    assert parts[0].part_number == 30


def test_lookup_part_nonexistent_number(db):
    assert lookup_part(db, "9999") == []


def test_lookup_part_nonexistent_keyword(db):
    assert lookup_part(db, "flux capacitor") == []


def test_get_manual_page_metadata_known_page():
    meta = get_manual_page_metadata("owner-manual", 24)
    assert meta is not None
    assert meta["section"] == "TIG / Stick Welding"
    assert meta["image_path"].endswith("page_024.png")


def test_get_manual_page_metadata_out_of_range_returns_none():
    assert get_manual_page_metadata("owner-manual", 999) is None


def test_get_manual_page_metadata_unknown_doc_returns_none():
    assert get_manual_page_metadata("nonexistent-doc", 1) is None
