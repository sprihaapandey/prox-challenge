from retrieval.semantic import search_visuals


def test_visual_search_returns_relevant_page(db):
    results = search_visuals(db, "duty cycle dial chart", limit=5)
    assert len(results) > 0
    pages = [r.page for r in results]
    assert any(p in (7, 19, 29) for p in pages), f"expected a duty-cycle chart page, got {pages}"


def test_visual_search_polarity_diagram(db):
    results = search_visuals(db, "TIG torch and ground clamp socket connections", limit=5)
    assert len(results) > 0
    assert any(r.doc_id in ("owner-manual", "quick-start-guide") for r in results)


def test_visual_search_selection_chart_reachable(db):
    """The selection chart has no text layer at all -- it must be findable via
    its vision-generated description, or knowledge from that page is lost."""
    results = search_visuals(db, "how to choose between MIG flux-cored TIG and stick", doc_id="selection-chart", limit=3)
    assert len(results) > 0


def test_visual_search_result_shape(db):
    results = search_visuals(db, "wire feed mechanism", limit=3)
    for r in results:
        assert r.image_path
        assert r.type in ("diagram", "schematic", "chart", "photo", "table", "illustration")
        assert isinstance(r.highlight_bbox_pct, list)
