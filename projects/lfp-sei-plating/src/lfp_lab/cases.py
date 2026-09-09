"""Build versioned PyBaMM cases from checked-in configurations."""

from __future__ import annotations

import re
from copy import deepcopy
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import pybamm

from .config import PROJECT_ROOT, load_case_config, load_parameter_provenance


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


def _record_parameter_blocker(message: str) -> None:
    """Append a fail-loudly parameter boundary violation to repository STATUS.md."""
    status_path = PROJECT_ROOT.parents[1] / "STATUS.md"
    timestamp = datetime.now(UTC).isoformat()
    with status_path.open("a", encoding="utf-8", newline="\n") as status:
        status.write("\n## 自动记录的参数阻塞\n\n")
        status.write(f"- {timestamp}：SEI/析锂参数边界检查失败：{message}\n")


def _missing_parameter_name(error: KeyError) -> str | None:
    match = re.search(r"Parameter '([^']+)' not found", str(error))
    return match.group(1) if match else None


def _borrow_side_reaction_parameters(
    model: pybamm.BaseModel, config: dict[str, Any]
) -> tuple[pybamm.ParameterValues, tuple[dict[str, str], ...]]:
    """Borrow only the machine-readable, side-reaction-specific allowlist."""
    provenance = load_parameter_provenance()
    allowed_categories = set(provenance["allowed_categories"])
    if allowed_categories != {"sei", "lithium_plating"}:
        message = "provenance categories must be exactly sei and lithium_plating"
        _record_parameter_blocker(message)
        raise RuntimeError(message)

    base = pybamm.ParameterValues(config["body_parameter_set"])
    donor = pybamm.ParameterValues(config["side_reaction_parameter_set"])
    borrowed: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in provenance["parameters"]:
        name = item["name"]
        category = item["category"]
        if name in seen or category not in allowed_categories:
            message = f"invalid or duplicate allowlist entry: {name} ({category})"
            _record_parameter_blocker(message)
            raise RuntimeError(message)
        if name in base:
            message = f"allowlist entry unexpectedly exists in the body set: {name}"
            _record_parameter_blocker(message)
            raise RuntimeError(message)
        if name not in donor:
            message = f"allowlist entry is absent from the donor set: {name}"
            _record_parameter_blocker(message)
            raise RuntimeError(message)
        seen.add(name)
        base.update({name: donor[name]}, check_already_exists=False)
        borrowed.append(
            {
                "name": name,
                "category": category,
                "dependency": item["dependency"],
                "source_parameter_set": config["side_reaction_parameter_set"],
                "base_parameter_set": config["body_parameter_set"],
                "confidence": config["confidence"],
            }
        )

    temperature_k = config["temperature_c"] + 273.15
    base.update(
        {
            "Ambient temperature [K]": temperature_k,
            "Initial temperature [K]": temperature_k,
        }
    )
    try:
        base.process_model(model, inplace=False)
    except KeyError as error:
        missing = _missing_parameter_name(error)
        label = missing or str(error).splitlines()[-1]
        message = f"unapproved required parameter: {label}"
        _record_parameter_blocker(message)
        raise RuntimeError(message) from error
    return base, tuple(borrowed)


def build_sei_plating_demo(
    *, cycles: int | None = None, quick: bool = False
) -> CaseDefinition:
    """Build the explicitly unvalidated hybrid-parameter degradation demo."""
    config = deepcopy(load_case_config("sei_plating_demo"))
    cycle_count = cycles if cycles is not None else config["cycles"]
    if cycle_count < 1:
        raise ValueError("Cycle count must be positive")
    if quick:
        config["experiment"] = [
            "Charge at 2C for 2 minutes",
            "Rest for 1 minute",
            "Discharge at 1C for 2 minutes",
            "Rest for 1 minute",
        ]
        config["period"] = "1 minute"
        config["mesh_points"] = {
            "x_n": 10,
            "x_s": 6,
            "x_p": 10,
            "r_n": 10,
            "r_p": 10,
        }
        config["run_profile"] = "short_smoke_test"
        cycle_count = 1
    else:
        config["run_profile"] = "full"
    config["effective_cycles"] = cycle_count

    model = pybamm.lithium_ion.DFN(
        options=config["model_options"],
        name="Prada2013 body with OKane2022 SEI/plating parameters",
    )
    parameter_values, borrowed = _borrow_side_reaction_parameters(model, config)
    return CaseDefinition(
        name="sei_plating_demo",
        model=model,
        parameter_values=parameter_values,
        experiment=_experiment(config, cycles=cycle_count),
        solver=_solver(config),
        initial_soc=config["initial_soc"],
        config=config,
        borrowed_parameters=borrowed,
    )


def build_case(case_name: str, *, cycles: int | None = None, quick: bool = False) -> CaseDefinition:
    """Build a named case without silently substituting another model."""
    if case_name == "baseline":
        if cycles not in (None, 1):
            raise ValueError("The baseline case is defined as one reference cycle")
        return build_baseline(quick=quick)
    if case_name == "sei_plating_demo":
        return build_sei_plating_demo(cycles=cycles, quick=quick)
    raise ValueError(f"Unknown case {case_name!r}")
