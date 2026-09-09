"""Build versioned PyBaMM cases from checked-in configurations."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

import pybamm

from .config import load_case_config


@dataclass(frozen=True)
class CaseDefinition:
    """All objects and metadata needed for one simulation."""

    name: str
    model: pybamm.BaseModel
    parameter_values: pybamm.ParameterValues
    experiment: pybamm.Experiment
    solver: pybamm.BaseSolver
    initial_soc: float
    config: dict[str, Any]
    borrowed_parameters: tuple[dict[str, str], ...] = ()


def _solver(config: dict[str, Any]) -> pybamm.IDAKLUSolver:
    settings = config["solver"]
    return pybamm.IDAKLUSolver(atol=settings["atol"], rtol=settings["rtol"])


def _experiment(config: dict[str, Any], cycles: int = 1) -> pybamm.Experiment:
    cycle = tuple(config["experiment"])
    return pybamm.Experiment(
        [cycle for _ in range(cycles)],
        period=config["period"],
        temperature=config["temperature_c"] + 273.15,
    )


def build_baseline(*, quick: bool = False) -> CaseDefinition:
    """Build the isothermal Prada2013 LFP/graphite DFN baseline."""
    config = deepcopy(load_case_config("baseline"))
    if quick:
        config["experiment"] = [
            "Discharge at 1C for 2 minutes",
            "Rest for 1 minute",
            "Charge at C/2 for 2 minutes",
            "Rest for 1 minute",
        ]
        config["period"] = "1 minute"
        config["run_profile"] = "short_smoke_test"
        config["mesh_points"] = {
            "x_n": 10,
            "x_s": 6,
            "x_p": 10,
            "r_n": 10,
            "r_p": 10,
        }
    else:
        config["run_profile"] = "full"

    options = {"thermal": "isothermal"}
    model = pybamm.lithium_ion.DFN(options=options, name="Prada2013 LFP/graphite DFN")
    parameter_values = pybamm.ParameterValues(config["parameter_set"])
    temperature_k = config["temperature_c"] + 273.15
    parameter_values.update(
        {
            "Ambient temperature [K]": temperature_k,
            "Initial temperature [K]": temperature_k,
        }
    )
    return CaseDefinition(
        name="baseline",
        model=model,
        parameter_values=parameter_values,
        experiment=_experiment(config),
        solver=_solver(config),
        initial_soc=config["initial_soc"],
        config=config,
    )


def build_case(case_name: str, *, cycles: int | None = None, quick: bool = False) -> CaseDefinition:
    """Build a named case without silently substituting another model."""
    if case_name == "baseline":
        if cycles not in (None, 1):
            raise ValueError("The baseline case is defined as one reference cycle")
        return build_baseline(quick=quick)
    if case_name == "sei_plating_demo":
        raise NotImplementedError("SEI/plating demo is added in the next implementation stage")
    raise ValueError(f"Unknown case {case_name!r}")
