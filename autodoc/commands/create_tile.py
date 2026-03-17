"""
create-tile command — Section 10 of AutoDoc V1 spec.

Flow:
 1. read tile_config.yaml
 2. obtain next global tile_number from tile_index.csv
 3. generate tile_id
 4. create database/tiles/<tile_id>/
 5. create README.md
 6. create works/
 7. create runs/
 8. add row to tile_index.csv
"""
from pathlib import Path

import yaml

from core.validator import (
    AutoDocError,
    validate_create_tile_structure,
    validate_tile_index_csv,
    validate_tile_config_fields,
)
from core.tile_id import generate_tile_id
from core.csv_store import next_tile_number, append_tile_index_row
from models.tile_config import TileConfig
from generators.readme import write_readme


def _load_tile_config(config_path: Path) -> TileConfig:
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return TileConfig.from_dict(raw)


def _gitkeep(directory: Path) -> None:
    """Place a .gitkeep in a directory so git tracks it when empty."""
    (directory / ".gitkeep").touch()


def run_create_tile(db_root: Path) -> None:
    """
    Execute the create-tile flow.
    db_root is the path to the `database/` directory.
    """
    # ── 16.1 validate required paths ──────────────────────────────────────
    validate_create_tile_structure(db_root)

    tile_index_path = db_root / "tile_index.csv"
    validate_tile_index_csv(tile_index_path)

    # ── 1. read tile_config.yaml ──────────────────────────────────────────
    config_path = db_root / "config" / "tile_config.yaml"
    cfg = _load_tile_config(config_path)

    # ── 16.2 validate id_version / id_revision ───────────────────────────
    validate_tile_config_fields(cfg.id_version, cfg.id_revision)

    # ── 2. obtain next tile_number ────────────────────────────────────────
    tile_number = next_tile_number(tile_index_path)

    # ── 3. generate tile_id ───────────────────────────────────────────────
    tile_id = generate_tile_id(
        id_prefix=cfg.id_prefix,
        id_version=cfg.id_version,
        id_revision=cfg.id_revision,
        tile_number=tile_number,
    )

    # ── collision guard (section 10 note) ─────────────────────────────────
    tile_root = db_root / "tiles" / tile_id
    if tile_root.exists():
        raise AutoDocError(
            f"Tile ID collision: '{tile_id}' already exists at {tile_root}."
        )

    # ── 4. create tile root directory ─────────────────────────────────────
    tile_root.mkdir(parents=True)
    print(f"[create-tile] Created tile directory: {tile_root}")

    # ── 5. create README.md ───────────────────────────────────────────────
    write_readme(tile_root, tile_id, cfg)
    print(f"[create-tile] README.md written.")

    # ── 6. create works/ ──────────────────────────────────────────────────
    works_root = tile_root / "works"
    for subdir in ("rtl", "tb", "constraints", "scripts"):
        cat_dir = works_root / subdir
        cat_dir.mkdir(parents=True)
        _gitkeep(cat_dir)
    print(f"[create-tile] works/ structure created.")

    # ── 7. create runs/ ───────────────────────────────────────────────────
    runs_dir = tile_root / "runs"
    runs_dir.mkdir()
    _gitkeep(runs_dir)
    print(f"[create-tile] runs/ directory created.")

    # ── 8. append to tile_index.csv ───────────────────────────────────────
    append_tile_index_row(
        tile_index_path,
        tile_number=tile_number,
        tile_id=tile_id,
        tile_name=cfg.tile_name,
        tile_author=cfg.tile_author,
    )
    print(f"[create-tile] tile_index.csv updated.")

    print(f"\n✓ Tile created successfully.")
    print(f"  Tile ID  : {tile_id}")
    print(f"  Name     : {cfg.tile_name}")
    print(f"  Author   : {cfg.tile_author}")
    print(f"  Path     : {tile_root}")
