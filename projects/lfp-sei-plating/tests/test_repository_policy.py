import subprocess
from pathlib import Path


def test_tracked_paths_use_english_ascii_names() -> None:
    repository_root = Path(__file__).resolve().parents[3]
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=repository_root,
        check=True,
        capture_output=True,
    )
    tracked_paths = [
        raw_path.decode("utf-8") for raw_path in result.stdout.split(b"\0") if raw_path
    ]
    invalid_paths = [
        path for path in tracked_paths if not path.isascii() or " " in path
    ]

    assert not invalid_paths, (
        "Tracked paths must use English ASCII names without spaces: "
        + ", ".join(invalid_paths)
    )
