from retrieval.semantic import search_chunks


def test_manual_search_returns_relevant_page(db):
    results = search_chunks(db, "how do I connect the TIG torch cable", limit=5)
    assert len(results) > 0
    pages = [r.page for r in results]
    assert 24 in pages, f"expected TIG Setup page 24 in top results, got {pages}"


def test_manual_search_duty_cycle_query(db):
    results = search_chunks(db, "duty cycle percentage at 200 amps", limit=5)
    pages = [r.page for r in results]
    assert any(p in (7, 19, 29) for p in pages)


def test_manual_search_respects_doc_id_filter(db):
    results = search_chunks(db, "welding process", doc_id="owner-manual", limit=5)
    assert all(r.doc_id == "owner-manual" for r in results)


def test_manual_search_relevance_is_normalized(db):
    results = search_chunks(db, "wire feed speed", limit=3)
    for r in results:
        assert 0.0 <= r.relevance <= 1.0


def test_manual_search_empty_query_does_not_crash(db):
    results = search_chunks(db, "", limit=3)
    assert isinstance(results, list)
