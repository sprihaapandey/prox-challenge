"""Verified against the owner's manual Specifications table, page 7, by hand."""

from retrieval.structured import lookup_duty_cycle

EXPECTED = {
    ("MIG", 120, 100): 40,
    ("MIG", 120, 75): 100,
    ("MIG", 240, 200): 25,
    ("MIG", 240, 115): 100,
    ("TIG", 120, 125): 40,
    ("TIG", 120, 90): 100,
    ("TIG", 240, 175): 30,
    ("TIG", 240, 105): 100,
    ("Stick", 120, 80): 40,
    ("Stick", 120, 60): 100,
    ("Stick", 240, 175): 25,
    ("Stick", 240, 100): 100,
}


def test_duty_cycle_lookup_exact_match(db):
    result = lookup_duty_cycle(db, "MIG", 240, 200)
    assert result["found"] is True
    assert result["duty_cycle_percent"] == 25
    assert result["source_page"] == 7


def test_duty_cycle_lookup_all_known_combinations(db):
    for (process, voltage, amperage), expected_percent in EXPECTED.items():
        result = lookup_duty_cycle(db, process, voltage, amperage)
        assert result["found"] is True, f"{process} {voltage}V {amperage}A should be found"
        assert result["duty_cycle_percent"] == expected_percent


def test_duty_cycle_lookup_flux_cored_shares_mig_spec(db):
    """The manual only tabulates duty cycle under 'MIG'; Flux-Cored shares that
    power-source rating (they differ in wire/gas/polarity, not output current)."""
    result = lookup_duty_cycle(db, "Flux-Cored", 240, 200)
    assert result["found"] is True
    assert result["duty_cycle_percent"] == 25
    assert "MIG" in result["note"]


def test_missing_duty_cycle_out_of_range(db):
    """Stick only goes up to 175A at 240V -- 200A doesn't exist in the manual."""
    result = lookup_duty_cycle(db, "Stick", 240, 200)
    assert result["found"] is False
    assert "does not provide" in result["message"]
    available = result["available_data_points_for_this_process_and_voltage"]
    assert len(available) == 2
    assert {d["amperage"] for d in available} == {175, 100}


def test_duty_cycle_malformed_negative_amperage(db):
    result = lookup_duty_cycle(db, "MIG", 240, -50)
    assert result["found"] is False
    assert "available_data_points_for_this_process_and_voltage" in result


def test_duty_cycle_malformed_unknown_process(db):
    result = lookup_duty_cycle(db, "Laser", 240, 200)
    assert result["found"] is False
