"""
init command — creates the full database/ skeleton.

Creates:
  database/
  ├── tile_index.csv        ← empty, header written on first use
  ├── records.csv           ← empty, header written on first use
  ├── tiles/                ← empty, tiles go here
  └── config/
      ├── tile_config.yaml  ← template ready to fill
      └── run_config.yaml   ← template ready to fill
"""
from pathlib import Path

from core.validator import AutoDocError


_TILE_CONFIG_TEMPLATE = """\
id_prefix: ""        # e.g. MST130-01
id_version: ""       # exactly 2 digits, e.g. 01
id_revision: ""      # exactly 2 digits, e.g. 01

tile_name: ""        # descriptive name of the tile
tile_author: ""      # author(s)

description: |
  

ports: |
  

usage_guide: |
  

tb_description: |
  
"""

_RUN_CONFIG_TEMPLATE = """\
run_author: ""
objective: ""
status: ""           # PASS | FAIL | WIP | EXCLUDE

vivado_version: ""
sim: ""              # e.g. xsim
top: ""              # top module name in testbench
seed: ""
sim_time: ""         # e.g. 1000ns
constraints_used: false
tags: ""

summary: |
  

key_warnings: |
  

key_errors: |
  

main_change: |
  

notes: |
  
"""


def run_init_db(db_root: Path, force: bool = False) -> None:
    """
    Create the database/ skeleton at db_root.

    If db_root already exists and force=False, raises AutoDocError.
    If force=True, skips existing files/folders without overwriting them.
    """
    if db_root.exists() and not force:
        raise AutoDocError(
            f"Directory already exists: {db_root}\n"
            "Use --force to initialize inside an existing directory."
        )

    db_root.mkdir(parents=True, exist_ok=True)
    print(f"[init] Database root: {db_root}")

    # ── tiles/ ────────────────────────────────────────────────────────────
    tiles_dir = db_root / "tiles"
    tiles_dir.mkdir(exist_ok=True)
    _gitkeep(tiles_dir)
    print(f"[init] Created tiles/")

    # ── config/ ───────────────────────────────────────────────────────────
    config_dir = db_root / "config"
    config_dir.mkdir(exist_ok=True)
    print(f"[init] Created config/")

    # ── tile_config.yaml ──────────────────────────────────────────────────
    tile_cfg_path = config_dir / "tile_config.yaml"
    if not tile_cfg_path.exists():
        tile_cfg_path.write_text(_TILE_CONFIG_TEMPLATE, encoding="utf-8")
        print(f"[init] Created config/tile_config.yaml")
    else:
        print(f"[init] Skipped config/tile_config.yaml (already exists)")

    # ── run_config.yaml ───────────────────────────────────────────────────
    run_cfg_path = config_dir / "run_config.yaml"
    if not run_cfg_path.exists():
        run_cfg_path.write_text(_RUN_CONFIG_TEMPLATE, encoding="utf-8")
        print(f"[init] Created config/run_config.yaml")
    else:
        print(f"[init] Skipped config/run_config.yaml (already exists)")

    # ── tile_index.csv ────────────────────────────────────────────────────
    tile_index_path = db_root / "tile_index.csv"
    if not tile_index_path.exists():
        tile_index_path.write_text("", encoding="utf-8")
        print(f"[init] Created tile_index.csv")
    else:
        print(f"[init] Skipped tile_index.csv (already exists)")

    # ── records.csv ───────────────────────────────────────────────────────
    records_path = db_root / "records.csv"
    if not records_path.exists():
        records_path.write_text("", encoding="utf-8")
        print(f"[init] Created records.csv")
    else:
        print(f"[init] Skipped records.csv (already exists)")

    print(f"\n✓ Database initialized successfully.")
    print(f"  Path : {db_root}")
    print(f"\nNext steps:")
    print(f"  1. Fill in config/tile_config.yaml")
    print(f"  2. Paste your Vivado project inside config/")
    print(f"  3. Run: python cli.py --db \"{db_root}\" create-tile")


def _gitkeep(directory: Path) -> None:
    (directory / ".gitkeep").touch()
