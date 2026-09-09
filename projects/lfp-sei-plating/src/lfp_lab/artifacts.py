"""Create portable, machine-readable run artifacts."""

from __future__ import annotations

import json
import logging
import platform
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pybamm

from .cases import CaseDefinition
from .config import PROJECT_ROOT, config_hash

LOGGER = logging.getLogger("lfp_lab")


@dataclass(frozen=True)
class RunResult:
    """A completed simulation and its exported artifacts."""

    output_dir: Path
    solution: pybamm.Solution
    manifest: dict[str, Any]
    timeseries: pd.DataFrame
    summary: pd.DataFrame


SERIES_VARIABLES = {
    "current_A": "Current [A]",
    "voltage_V": "Voltage [V]",
    "discharge_capacity_Ah": "Discharge capacity [A.h]",
    "charge_capacity_Ah": "Charge capacity [A.h]",
    "loss_of_lithium_inventory_pct": "Loss of lithium inventory [%]",
    "sei_capacity_loss_Ah": "Loss of capacity to negative SEI [A.h]",
    "plating_capacity_loss_Ah": "Loss of capacity to negative lithium plating [A.h]",
    "negative_sei_thickness_m": "X-averaged negative SEI thickness [m]",
    "plated_lithium_concentration_mol_m3": (
        "X-averaged negative lithium plating concentration [mol.m-3]"
    ),
    "dead_lithium_concentration_mol_m3": (
        "X-averaged negative dead lithium concentration [mol.m-3]"
    ),
}


def _entries(solution: pybamm.Solution, variable_name: str) -> np.ndarray | None:
    try:
        values = np.asarray(solution[variable_name].entries, dtype=float).squeeze()
    except KeyError:
        return None
    if values.ndim != 1 or values.size != solution.t.size:
        return None
    return values


def solution_timeseries(solution: pybamm.Solution) -> pd.DataFrame:
    """Extract required scalar time histories with strictly increasing time."""
    time_s = np.asarray(solution.t, dtype=float)
    keep = np.concatenate(([True], np.diff(time_s) > 0))
    data: dict[str, np.ndarray] = {
        "time_s": time_s[keep],
        "time_h": time_s[keep] / 3600,
    }
    for column, variable_name in SERIES_VARIABLES.items():
        values = _entries(solution, variable_name)
        if values is not None:
            data[column] = values[keep]
    return pd.DataFrame(data)


def _final(cycle: pybamm.Solution, variable_name: str) -> float:
    values = _entries(cycle, variable_name)
    return float(values[-1]) if values is not None else float("nan")


def _maximum(cycle: pybamm.Solution, variable_name: str) -> float:
    values = _entries(cycle, variable_name)
    return float(np.nanmax(values)) if values is not None else float("nan")


def _integrated_capacity(cycle: pybamm.Solution, *, discharge: bool) -> float:
    """Integrate one cycle's discharge or charge current into positive ampere-hours."""
    current = _entries(cycle, "Current [A]")
    if current is None:
        return float("nan")
    signed_current = np.maximum(current, 0) if discharge else np.maximum(-current, 0)
    return float(np.trapezoid(signed_current, np.asarray(cycle.t, dtype=float)) / 3600)


def solution_summary(solution: pybamm.Solution) -> pd.DataFrame:
    """Create one compact row per experiment cycle."""
    rows: list[dict[str, float | int]] = []
    cycles = solution.cycles or [solution]
    for index, cycle in enumerate(cycles, start=1):
        cycle_time = np.asarray(cycle.t, dtype=float)
        rows.append(
            {
                "cycle_index": index,
                "start_time_h": float(cycle_time[0] / 3600),
                "end_time_h": float(cycle_time[-1] / 3600),
                "duration_h": float((cycle_time[-1] - cycle_time[0]) / 3600),
                "final_voltage_V": _final(cycle, "Voltage [V]"),
                "discharge_capacity_Ah": _integrated_capacity(cycle, discharge=True),
                "charge_capacity_Ah": _integrated_capacity(cycle, discharge=False),
                "loss_of_lithium_inventory_pct": _final(
                    cycle, "Loss of lithium inventory [%]"
                ),
                "sei_capacity_loss_Ah": _final(
                    cycle, "Loss of capacity to negative SEI [A.h]"
                ),
                "plating_capacity_loss_Ah": _final(
                    cycle, "Loss of capacity to negative lithium plating [A.h]"
                ),
                "max_plated_lithium_concentration_mol_m3": _maximum(
                    cycle, "X-averaged negative lithium plating concentration [mol.m-3]"
                ),
            }
        )
    return pd.DataFrame(rows)


def _make_output_dir(case: CaseDefinition, output_root: Path | None) -> Path:
    root = output_root or PROJECT_ROOT / "results" / "runs"
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S.%fZ")
    output_dir = root / case.name / f"{timestamp}-{config_hash(case.config)}"
    output_dir.mkdir(parents=True, exist_ok=False)
    return output_dir


def _plot(timeseries: pd.DataFrame, output_dir: Path, confidence: str) -> list[str]:
    fig, axes = plt.subplots(3, 1, figsize=(10, 9), sharex=True, constrained_layout=True)
    axes[0].plot(timeseries["time_h"], timeseries["voltage_V"], color="#1f77b4")
    axes[0].set_ylabel("Voltage / V")
    axes[1].plot(timeseries["time_h"], timeseries["current_A"], color="#d62728")
    axes[1].set_ylabel("Current / A")
    axes[2].plot(
        timeseries["time_h"], timeseries["discharge_capacity_Ah"], color="#2ca02c"
    )
    axes[2].set_ylabel("Discharge capacity / Ah")
    axes[2].set_xlabel("Time / h")
    fig.suptitle(f"PyBaMM run — {confidence}")
    if confidence == "illustrative_unvalidated":
        fig.text(
            0.5,
            0.5,
            "ILLUSTRATIVE · UNVALIDATED",
            ha="center",
            va="center",
            fontsize=25,
            color="crimson",
            alpha=0.18,
            rotation=25,
        )
    fig.savefig(output_dir / "overview.png", dpi=160)
    plt.close(fig)
    artifacts = ["overview.png"]

    degradation_columns = [
        ("sei_capacity_loss_Ah", "SEI capacity loss / Ah"),
        ("plating_capacity_loss_Ah", "Plating capacity loss / Ah"),
        ("plated_lithium_concentration_mol_m3", "Plated Li / mol m$^{-3}$"),
    ]
    if all(column in timeseries for column, _ in degradation_columns):
        fig, axes = plt.subplots(
            len(degradation_columns), 1, figsize=(10, 9), sharex=True, constrained_layout=True
        )
        for axis, (column, ylabel) in zip(axes, degradation_columns, strict=True):
            axis.plot(timeseries["time_h"], timeseries[column])
            axis.set_ylabel(ylabel)
        axes[-1].set_xlabel("Time / h")
        fig.suptitle("illustrative_unvalidated — hybrid-parameter degradation signals")
        fig.text(
            0.5,
            0.5,
            "ILLUSTRATIVE · UNVALIDATED",
            ha="center",
            va="center",
            fontsize=25,
            color="crimson",
            alpha=0.18,
            rotation=25,
        )
        fig.savefig(output_dir / "degradation.png", dpi=160)
        plt.close(fig)
        artifacts.append("degradation.png")
    return artifacts


def execute_case(case: CaseDefinition, *, output_root: Path | None = None) -> RunResult:
    """Solve one case and write the complete artifact bundle."""
    output_dir = _make_output_dir(case, output_root)
    log_path = output_dir / "run.log"
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    LOGGER.addHandler(handler)
    LOGGER.setLevel(logging.INFO)
    started = datetime.now(UTC)
    timer = time.perf_counter()
    try:
        LOGGER.info("Starting case %s", case.name)
        simulation = pybamm.Simulation(
            case.model,
            parameter_values=case.parameter_values,
            experiment=case.experiment,
            solver=case.solver,
            var_pts=case.config["mesh_points"],
        )
        solution = simulation.solve(initial_soc=case.initial_soc, showprogress=False)
        elapsed_s = time.perf_counter() - timer
        timeseries = solution_timeseries(solution)
        summary = solution_summary(solution)
        timeseries.to_csv(output_dir / "timeseries.csv", index=False)
        summary.to_csv(output_dir / "summary.csv", index=False)
        confidence = case.config["confidence"]
        plot_artifacts = _plot(timeseries, output_dir, confidence)
        manifest: dict[str, Any] = {
            "schema_version": 1,
            "run_status": "success",
            "case": case.name,
            "confidence": confidence,
            "config_hash": config_hash(case.config),
            "configuration": case.config,
            "model_options": dict(case.model.options),
            "parameter_provenance": list(case.borrowed_parameters),
            "versions": {
                "lfp_lab": "0.1.0",
                "pybamm": pybamm.__version__,
                "python": platform.python_version(),
                "platform": platform.system(),
            },
            "started_at_utc": started.isoformat(),
            "finished_at_utc": datetime.now(UTC).isoformat(),
            "elapsed_s": elapsed_s,
            "termination": solution.termination,
            "completed_cycles": len(solution.cycles or []),
            "completed_steps": [len(cycle.steps) for cycle in (solution.cycles or [])],
            "artifacts": [
                "manifest.json",
                "timeseries.csv",
                "summary.csv",
                *plot_artifacts,
                "run.log",
            ],
        }
        (output_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        LOGGER.info("Finished case %s in %.3f s", case.name, elapsed_s)
        return RunResult(output_dir, solution, manifest, timeseries, summary)
    except Exception:
        LOGGER.exception("Case %s failed", case.name)
        failure = {
            "schema_version": 1,
            "run_status": "failed",
            "case": case.name,
            "config_hash": config_hash(case.config),
            "started_at_utc": started.isoformat(),
            "failed_at_utc": datetime.now(UTC).isoformat(),
            "python": sys.version,
        }
        (output_dir / "manifest.json").write_text(
            json.dumps(failure, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        raise
    finally:
        LOGGER.removeHandler(handler)
        handler.close()
