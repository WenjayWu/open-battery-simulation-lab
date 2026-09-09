"""Case configuration loading and stable hashing."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "configs"


def load_case_config(case_name: str) -> dict[str, Any]:
    """Load a checked-in JSON case configuration."""
    path = CONFIG_DIR / f"{case_name}.json"
    if not path.is_file():
        available = ", ".join(sorted(item.stem for item in CONFIG_DIR.glob("*.json")))
        raise ValueError(f"Unknown case {case_name!r}. Available cases: {available}")
    return json.loads(path.read_text(encoding="utf-8"))


def config_hash(config: dict[str, Any]) -> str:
    """Return a stable short SHA-256 hash for a case configuration."""
    canonical = json.dumps(config, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]
