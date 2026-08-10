"""Verified against the owner's manual's per-process cable/socket diagrams:
MIG p.14, Flux-Cored p.13, TIG p.24, Stick p.27."""

from retrieval.structured import lookup_polarity

EXPECTED = {
    "MIG": {"gun_socket": "Positive", "ground_socket": "Negative", "page": 14},
    "Flux-Cored": {"gun_socket": "Negative", "ground_socket": "Positive", "page": 13},
    "TIG": {"gun_socket": "Negative", "ground_socket": "Positive", "page": 24},
    "Stick": {"gun_socket": "Positive", "ground_socket": "Negative", "page": 27},
}


def test_polarity_lookup_all_processes(db):
    for process, expected in EXPECTED.items():
        result = lookup_polarity(db, process)
        assert result["found"] is True, f"{process} should be found"
        assert result["gun_or_torch_or_electrode_socket"] == expected["gun_socket"]
        assert result["ground_clamp_socket"] == expected["ground_socket"]
        assert result["source_page"] == expected["page"]


def test_polarity_lookup_alias_normalization(db):
    variants = ["flux cored", "flux-cored", "FLUX CORED", "fluxcore", "fcaw"]
    for variant in variants:
        result = lookup_polarity(db, variant)
        assert result["found"] is True, f"{variant!r} should normalize to Flux-Cored"
        assert result["process"] == "Flux-Cored"


def test_polarity_ground_clamp_socket_differs_by_process(db):
    """This directly answers the challenge's example question -- the answer is
    NOT the same for every process, so a correct implementation must actually
    look it up rather than return one fixed answer."""
    mig = lookup_polarity(db, "MIG")
    flux = lookup_polarity(db, "Flux-Cored")
    assert mig["ground_clamp_socket"] != flux["ground_clamp_socket"]


def test_polarity_lookup_unknown_process(db):
    result = lookup_polarity(db, "Laser")
    assert result["found"] is False
    assert set(result["known_processes"]) == {"MIG", "Flux-Cored", "TIG", "Stick"}


def test_polarity_lookup_empty_string(db):
    result = lookup_polarity(db, "")
    assert result["found"] is False
