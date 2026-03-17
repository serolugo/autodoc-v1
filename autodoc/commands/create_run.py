"""
create-run command — Section 11 of AutoDoc V1 spec.

Flow:
  1.  verify target tile exists
  2.  read run_config.yaml
  3.  determine next run-NNN folder name
  4.  create run folder
  5.  create run internal structure
  6.  copy snapshot of run_config.yaml to run root
  7.  copy source files from Vivado project
  8.  copy generated artifacts from Vivado project
  9.  generate manifest.yaml
  10. generate notes.md
  11. regenerate tile README.md
  12. update works/
  13. append row to records.csv
"""
import shutil
from datetime import date
from pathlib import Path

import yaml

from core.validator import (
    AutoDocError,
    validate_create_run_structure,
    validate_tile_index_csv,
    validate_records_csv,
    validate_run_status,
    validate_tile_exists,
)
from core.run_id import next_run_id, latest_run_folder
from core.copier import copy_sources, copy_artifacts
from core.csv_store import append_records_row
from models.tile_config import TileConfig
from models.run_config import RunConfig
from generators.readme import write_readme
from generators.notes import write_notes
from generators.manifest import build_manifest, write_manifest


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _find_vivado_dir(config_dir: Path) -> Path:
    """Return the single project subdirectory inside config/."""
    subdirs = [p for p in config_dir.iterdir() if p.is_dir()]
    if not subdirs:
        raise AutoDocError(f"No VivadoProject directory found inside {config_dir}")
    return sorted(subdirs)[0]


def _gitkeep(directory: Path) -> None:
    """Place a .gitkeep in a directory so git tracks it when empty."""
    (directory / ".gitkeep").touch()


def _create_run_structure(run_root: Path) -> None:
    """Section 12 — create the full run folder tree with .gitkeep in each dir."""
    for path in (
        run_root / "src" / "rtl",
        run_root / "src" / "tb",
        run_root / "src" / "constraints",
        run_root / "src" / "scripts",
        run_root / "out" / "sim"   / "logs",
        run_root / "out" / "sim"   / "waves",
        run_root / "out" / "synth" / "logs",
        run_root / "out" / "synth" / "reports",
        run_root / "out" / "impl"  / "logs",
        run_root / "out" / "impl"  / "reports",
    ):
        path.mkdir(parents=True, exist_ok=True)
        _gitkeep(path)


def _update_works(tile_root: Path, run_src: Path) -> None:
    """
    Section 13 — update works/:
      - clear all contents inside works/ (keep the folder itself)
      - copy src/ contents from latest run (flat by category)
    """
    works_root = tile_root / "works"

    # Clear contents, keep the folder and its category subdirs
    for cat_dir in works_root.iterdir():
        if cat_dir.is_dir():
            shutil.rmtree(cat_dir)
            cat_dir.mkdir()

    # Copy flat by category from the run's src/
    for cat in ("rtl", "tb", "constraints", "scripts"):
        src_cat = run_src / cat
        dst_cat = works_root / cat
        dst_cat.mkdir(exist_ok=True)
        if src_cat.exists():
            for f in src_cat.iterdir():
                if f.is_file():
                    shutil.copy2(f, dst_cat / f.name)


def run_create_run(db_root: Path, tile_id: str) -> None:
    """
    Execute the create-run flow for the given tile_id.
    db_root is the path to the `database/` directory.
    """
    today = date.today().strftime("%Y-%m-%d")

    # ── 16.1 validate structure ──────────────────────────────────────────
    validate_create_run_structure(db_root)

    tile_index_path = db_root / "tile_index.csv"
    records_path    = db_root / "records.csv"

    validate_tile_index_csv(tile_index_path)
    validate_records_csv(records_path)

    tiles_root = db_root / "tiles"

    # ── 1. verify tile exists ────────────────────────────────────────────
    validate_tile_exists(tiles_root, tile_id)
    tile_root = tiles_root / tile_id

    # ── 2. read configs ──────────────────────────────────────────────────
    config_dir   = db_root / "config"
    run_cfg_path = config_dir / "run_config.yaml"

    # tile_config.yaml is needed for README/notes regeneration
    tile_cfg_path = config_dir / "tile_config.yaml"
    tile_cfg = TileConfig.from_dict(_load_yaml(tile_cfg_path))
    run_cfg  = RunConfig.from_dict(_load_yaml(run_cfg_path))

    # ── 16.2 validate status ─────────────────────────────────────────────
    validate_run_status(run_cfg.status)

    vivado_dir = _find_vivado_dir(config_dir)

    # ── 3. determine next run id ─────────────────────────────────────────
    runs_dir = tile_root / "runs"
    run_id   = next_run_id(runs_dir)
    run_root = runs_dir / run_id

    print(f"[create-run] Starting {run_id} for tile {tile_id}")

    # ── 4 & 5. create run folder + internal structure ────────────────────
    run_root.mkdir(parents=True)
    _create_run_structure(run_root)
    print(f"[create-run] Run structure created at {run_root}")

    # ── 6. (snapshot of run_config.yaml not stored per spec update) ─────

    # ── 7. copy source files ─────────────────────────────────────────────
    copied_sources = copy_sources(vivado_dir, run_root / "src")
    for cat, files in copied_sources.items():
        print(f"[create-run] src/{cat}: {len(files)} file(s) copied.")

    # ── 8. copy generated artifacts ──────────────────────────────────────
    copied_artifacts = copy_artifacts(vivado_dir, run_root / "out")
    for key, files in copied_artifacts.items():
        print(f"[create-run] out/{key}: {len(files)} file(s) copied.")

    # ── 9. generate manifest.yaml ────────────────────────────────────────
    manifest = build_manifest(
        tile_id=tile_id,
        run_id=run_id,
        date=today,
        run_cfg=run_cfg,
        copied_sources=copied_sources,
        copied_artifacts=copied_artifacts,
        tiles_root=tiles_root,
    )
    write_manifest(run_root, manifest)
    print(f"[create-run] manifest.yaml generated.")

    # ── 10. generate notes.md ────────────────────────────────────────────
    write_notes(run_root, tile_id, tile_cfg, run_cfg)
    print(f"[create-run] notes.md generated.")

    # ── 11. regenerate tile README.md ────────────────────────────────────
    write_readme(tile_root, tile_id, tile_cfg)
    print(f"[create-run] README.md regenerated.")

    # ── 12. update works/ ────────────────────────────────────────────────
    _update_works(tile_root, run_root / "src")
    print(f"[create-run] works/ updated.")

    # ── 13. append to records.csv ────────────────────────────────────────
    # run_path relative to tiles/ (section 15)
    run_path_rel = f"tiles/{tile_id}/runs/{run_id}"

    append_records_row(
        records_path,
        tile_id=tile_id,
        run_id=run_id,
        date=today,
        author=run_cfg.run_author,
        objective=run_cfg.objective,
        status=run_cfg.status,
        main_change=run_cfg.main_change,
        run_path=run_path_rel,
        vivado_version=run_cfg.vivado_version,
        result_summary=run_cfg.summary,
        tags=run_cfg.tags,
    )
    print(f"[create-run] records.csv updated.")

    print(f"\n✓ Run created successfully.")
    print(f"  Tile ID  : {tile_id}")
    print(f"  Run ID   : {run_id}")
    print(f"  Status   : {run_cfg.status}")
    print(f"  Path     : {run_path_rel}")
