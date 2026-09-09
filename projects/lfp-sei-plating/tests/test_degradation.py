from __future__ import annotations

import numpy as np
import pybamm
import pytest

from lfp_lab.cases import build_case
from lfp_lab.run import run_case


def test_degradation_case_borrows_only_side_reaction_allowlist() -> None:
    case = build_case("sei_plating_demo", cycles=1)
    prada = pybamm.ParameterValues("Prada2013")

    assert case.config["body_parameter_set"] == "Prada2013"
    assert case.config["side_reaction_parameter_set"] == "OKane2022"
    assert case.config["confidence"] == "illustrative_unvalidated"
    assert len(case.borrowed_parameters) == 16
    assert {item["category"] for item in case.borrowed_parameters} == {
        "sei",
        "lithium_plating",
    }
    assert all(item["name"] not in prada for item in case.borrowed_parameters)
    assert case.model.options["SEI"][0] == "solvent-diffusion limited"
    assert case.model.options["lithium plating"][0] == "partially reversible"
    assert case.model.options["SEI porosity change"] == "true"
    assert case.model.options["lithium plating porosity change"] == "true"


@pytest.mark.integration
def test_short_degradation_smoke_exports_side_reaction_signals(tmp_path) -> None:
    result = run_case("sei_plating_demo", quick=True, output_root=tmp_path)

    assert result.manifest["confidence"] == "illustrative_unvalidated"
    assert result.manifest["completed_cycles"] == 1
    assert len(result.manifest["parameter_provenance"]) == 16
    assert "degradation.png" in result.manifest["artifacts"]
    required = {
        "loss_of_lithium_inventory_pct",
        "sei_capacity_loss_Ah",
        "plating_capacity_loss_Ah",
        "negative_sei_thickness_m",
        "plated_lithium_concentration_mol_m3",
        "dead_lithium_concentration_mol_m3",
    }
    assert required.issubset(result.timeseries.columns)
    assert np.isfinite(result.timeseries[list(required)].to_numpy()).all()
    assert result.summary.loc[0, "discharge_capacity_Ah"] > 0
    assert result.summary.loc[0, "charge_capacity_Ah"] > 0
