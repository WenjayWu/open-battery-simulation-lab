from __future__ import annotations

from lfp_lab.config import config_hash, load_case_config


def test_baseline_configuration_is_locked_to_approved_scope() -> None:
    config = load_case_config("baseline")

    assert config["model"] == "DFN"
    assert config["parameter_set"] == "Prada2013"
    assert config["temperature_c"] == 25.0
    assert config["initial_soc"] == 0.95
    assert config["experiment"] == [
        "Discharge at 1C until 2.5 V",
        "Rest for 30 minutes",
        "Charge at C/2 until 3.6 V",
        "Hold at 3.6 V until C/20",
        "Rest for 30 minutes",
    ]


def test_config_hash_is_stable_for_key_order() -> None:
    assert config_hash({"b": 2, "a": 1}) == config_hash({"a": 1, "b": 2})
