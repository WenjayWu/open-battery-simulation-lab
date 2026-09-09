from __future__ import annotations

import json

import numpy as np
import pytest

from lfp_lab.run import run_case


@pytest.mark.integration
def test_short_baseline_smoke_exports_valid_artifacts(tmp_path) -> None:
    result = run_case("baseline", quick=True, output_root=tmp_path)

    assert result.manifest["run_status"] == "success"
    assert result.manifest["versions"]["pybamm"] == "26.6.2.0"
    assert np.all(np.diff(result.timeseries["time_s"]) > 0)
    assert np.isfinite(result.timeseries["voltage_V"]).all()
    assert np.isfinite(result.timeseries["discharge_capacity_Ah"]).all()
    assert result.timeseries["voltage_V"].between(2.0, 4.0).all()
    assert set(
        ["manifest.json", "timeseries.csv", "summary.csv", "overview.png", "run.log"]
    ).issubset(item.name for item in result.output_dir.iterdir())
    manifest = json.loads((result.output_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["configuration"]["run_profile"] == "short_smoke_test"
