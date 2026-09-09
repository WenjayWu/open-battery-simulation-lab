from __future__ import annotations

import numpy as np
import pytest

from lfp_lab.run import run_case


@pytest.mark.integration
@pytest.mark.parametrize("case_name", ["baseline", "sei_plating_demo"])
def test_short_run_summary_is_reproducible(case_name, tmp_path) -> None:
    first = run_case(case_name, quick=True, output_root=tmp_path / "first")
    second = run_case(case_name, quick=True, output_root=tmp_path / "second")

    assert first.manifest["config_hash"] == second.manifest["config_hash"]
    columns = [
        "final_voltage_V",
        "discharge_capacity_Ah",
        "charge_capacity_Ah",
        "loss_of_lithium_inventory_pct",
        "sei_capacity_loss_Ah",
        "plating_capacity_loss_Ah",
    ]
    np.testing.assert_allclose(
        first.summary[columns].to_numpy(),
        second.summary[columns].to_numpy(),
        rtol=1e-6,
        atol=1e-12,
        equal_nan=True,
    )
