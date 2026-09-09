"""Command-line entry point for all checked-in simulation cases."""

from __future__ import annotations

import argparse
from pathlib import Path

from .artifacts import RunResult, execute_case
from .cases import build_case


def run_case(
    case_name: str,
    *,
    cycles: int | None = None,
    quick: bool = False,
    output_root: Path | None = None,
) -> RunResult:
    """Build, solve, and export one named case."""
    case = build_case(case_name, cycles=cycles, quick=quick)
    return execute_case(case, output_root=output_root)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", required=True, choices=("baseline", "sei_plating_demo"))
    parser.add_argument("--cycles", type=int, help="Override cycle count where supported")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run a shortened numerical smoke profile; never use it as scientific output",
    )
    parser.add_argument("--output-root", type=Path, help="Optional output root for tests or CI")
    return parser


def main() -> None:
    args = _parser().parse_args()
    result = run_case(
        args.case,
        cycles=args.cycles,
        quick=args.quick,
        output_root=args.output_root,
    )
    print(result.output_dir.resolve())


if __name__ == "__main__":
    main()
