from retrieval.structured import lookup_settings


def test_settings_lookup_known_process(db):
    result = lookup_settings("MIG")
    assert result["found"] is True
    assert result["capability"]["process"] == "MIG"
    assert "0.030" in "".join(result["capability"]["wire_diameters"])


def test_missing_setting_no_static_table_caveat_present(db):
    """This machine is synergic auto-set -- there is no printed 'material +
    thickness -> voltage + wire speed' table. The tool's result must make
    that explicit so the agent never invents specific numbers."""
    result = lookup_settings("MIG")
    assert "auto-set" in result["important_caveat"] or "synergic" in result["important_caveat"]


def test_settings_lookup_unknown_process(db):
    result = lookup_settings("Laser")
    assert result["found"] is False
    assert set(result["known_processes"]) == {"MIG", "Flux-Cored", "TIG", "Stick"}


def test_settings_lookup_empty_string(db):
    result = lookup_settings("")
    assert result["found"] is False
