"""
Validation rules — Section 16 of AutoDoc V1 spec.
"""
import re
from pathlib import Path

from models.run_config import VALID_STATUSES

TILE_INDEX_HEADER = ["tile_number", "tile_id", "tile_name", "tile_author"]
RECORDS_HEADER = [
    "Tile_ID", "Run_ID", "Date", "Author", "Objective", "Status",
    "Main_Change", "Run_Path", "Vivado_Version", "Result_Summary", "Tags",
]


class AutoDocError(Exception):
    """Hard error — stops execution."""


def require_path(path: Path, label: str) -> None:
    """Section 16.1 — mark error if missing."""
    if not path.exists():
        raise AutoDocError(f"Required path not found: {label} ({path})")


def validate_create_tile_structure(db_root: Path) -> None:
    """
    Validate paths required by create-tile (section 10 inputs + 16.1).
    - database/config/
    - database/tiles/
    - database/config/tile_config.yaml
    - tile_index.csv
    - records.csv
    """
    require_path(db_root / "config", "database/config/")
    require_path(db_root / "tiles", "database/tiles/")
    require_path(db_root / "config" / "tile_config.yaml", "database/config/tile_config.yaml")
    require_path(db_root / "tile_index.csv", "tile_index.csv")
    require_path(db_root / "records.csv", "records.csv")


def validate_create_run_structure(db_root: Path) -> None:
    """
    Validate paths required by create-run (section 11 inputs + 16.1).
    Extends create-tile checks with run_config.yaml and VivadoProject/.
    """
    validate_create_tile_structure(db_root)
    require_path(db_root / "config" / "run_config.yaml", "database/config/run_config.yaml")

    vivado_dirs = [p for p in (db_root / "config").iterdir() if p.is_dir()]
    if not vivado_dirs:
        raise AutoDocError(
            "Required path not found: database/config/VivadoProject/ "
            "(no subdirectory found inside database/config/)"
        )


def validate_csv_header(csv_path: Path, expected_header: list[str], label: str) -> None:
    """
    Section 16.2 — mark error if header is wrong when file is non-empty.
    Section 16.3 — skip validation if file is empty.
    """
    content = csv_path.read_text(encoding="utf-8").strip()
    if not content:
        return  # Section 16.3 / 16.4 — empty file is valid

    first_line = content.splitlines()[0]
    actual = [col.strip() for col in first_line.split(",")]
    if actual != expected_header:
        raise AutoDocError(
            f"Invalid CSV header in {label}.\n"
            f"  Expected : {expected_header}\n"
            f"  Found    : {actual}"
        )


def validate_tile_index_csv(csv_path: Path) -> None:
    validate_csv_header(csv_path, TILE_INDEX_HEADER, "tile_index.csv")


def validate_records_csv(csv_path: Path) -> None:
    validate_csv_header(csv_path, RECORDS_HEADER, "records.csv")


def validate_tile_config_fields(id_version: str, id_revision: str) -> None:
    """Section 16.2 — id_version and id_revision must be exactly 2 digits."""
    if not re.fullmatch(r"\d{2}", id_version):
        raise AutoDocError(
            f"Invalid id_version '{id_version}': must be exactly 2 digits (e.g. 01)."
        )
    if not re.fullmatch(r"\d{2}", id_revision):
        raise AutoDocError(
            f"Invalid id_revision '{id_revision}': must be exactly 2 digits (e.g. 02)."
        )


def validate_run_status(status: str) -> None:
    """Section 16.2 — status must be one of PASS | FAIL | WIP | EXCLUDE."""
    if status not in VALID_STATUSES:
        raise AutoDocError(
            f"Invalid status '{status}': must be one of {sorted(VALID_STATUSES)}."
        )


def validate_tile_exists(tiles_root: Path, tile_id: str) -> None:
    """Section 4 + 16.1 — tile must exist as a directory under tiles/."""
    tile_path = tiles_root / tile_id
    if not tile_path.is_dir():
        raise AutoDocError(
            f"Tile '{tile_id}' does not exist at {tile_path}. "
            "Run 'create-tile' first."
        )
