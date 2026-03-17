"""
Run ID logic — Section 6 of AutoDoc V1 spec.

Run folders follow the pattern run-NNN (three digits, e.g. run-001).
Only folders matching that exact pattern are considered valid.
The next run is max(existing) + 1, or run-001 if none exist.
"""
import re
from pathlib import Path

_RUN_PATTERN = re.compile(r"^run-(\d{3})$")


def list_valid_run_folders(runs_dir: Path) -> list[Path]:
    """Return all run folders matching run-\\d{3}, sorted ascending."""
    if not runs_dir.exists():
        return []
    return sorted(
        p for p in runs_dir.iterdir()
        if p.is_dir() and _RUN_PATTERN.match(p.name)
    )


def next_run_id(runs_dir: Path) -> str:
    """
    Determine the next run folder name.
    Returns 'run-001' if no valid runs exist.
    """
    existing = list_valid_run_folders(runs_dir)
    if not existing:
        return "run-001"

    last_name = existing[-1].name
    match = _RUN_PATTERN.match(last_name)
    last_num = int(match.group(1))
    return f"run-{last_num + 1:03d}"


def latest_run_folder(runs_dir: Path) -> Path | None:
    """Return the most recent valid run folder, or None."""
    existing = list_valid_run_folders(runs_dir)
    return existing[-1] if existing else None
