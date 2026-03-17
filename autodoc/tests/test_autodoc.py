"""
AutoDoc V1 — Integration tests.

Tests are run from the autodoc/ directory:
  cd autodoc && python -m pytest tests/

Covers:
- tile_id format (section 5)
- run_id detection (section 6)
- create-tile full flow (section 10)
- create-run full flow (section 11)
- works/ update (section 13)
- copy collision handling (section 14.3)
- CSV header validation (section 16.2)
- empty CSV handling (section 16.4)
- path persistence (section 15)
- validation errors (section 16)
"""
import csv
import shutil
from datetime import date
from pathlib import Path

import contextlib
import re as _re
import yaml


@contextlib.contextmanager
def raises(exc_type, match=None):
    """Minimal pytest.raises replacement."""
    try:
        yield
    except exc_type as e:
        if match and not _re.search(match, str(e)):
            raise AssertionError(
                f"Exception message {str(e)!r} does not match {match!r}"
            ) from e
    except Exception as e:
        raise AssertionError(f"Expected {exc_type.__name__}, got {type(e).__name__}: {e}") from e
    else:
        raise AssertionError(f"Expected {exc_type.__name__} to be raised")

# ── helpers ───────────────────────────────────────────────────────────────

def make_db(tmp_path: Path) -> Path:
    """Create a minimal valid database/ skeleton."""
    db = tmp_path / "database"
    (db / "config").mkdir(parents=True)
    (db / "tiles").mkdir()
    (db / "tile_index.csv").write_text("", encoding="utf-8")
    (db / "records.csv").write_text("", encoding="utf-8")
    return db


def write_tile_config(db: Path, overrides: dict | None = None) -> None:
    data = {
        "id_prefix":    "TST",
        "id_version":   "01",
        "id_revision":  "02",
        "tile_name":    "Test Tile",
        "tile_author":  "Test Author",
        "ports":        "port_a, port_b",
        "usage_guide":  "Connect to bus.",
        "tb_description": "Stimulus from file.",
    }
    if overrides:
        data.update(overrides)
    path = db / "config" / "tile_config.yaml"
    path.write_text(yaml.dump(data), encoding="utf-8")


def write_run_config(db: Path, overrides: dict | None = None) -> None:
    data = {
        "run_author":    "Runner",
        "objective":     "Smoke test",
        "status":        "PASS",
        "vivado_version": "2023.2",
        "sim":           "xsim",
        "top":           "top_tb",
        "seed":          "42",
        "sim_time":      "1000ns",
        "constraints_used": False,
        "tags":          "smoke baseline",
        "summary":       "All OK",
        "key_warnings":  "none",
        "key_errors":    "none",
        "main_change":   "Initial run",
        "notes":         "First documented run",
    }
    if overrides:
        data.update(overrides)
    path = db / "config" / "run_config.yaml"
    path.write_text(yaml.dump(data), encoding="utf-8")


def make_vivado_project(db: Path, project_name: str = "my_proj") -> Path:
    """
    Create a minimal fake Vivado project structure with sample files.

    Layout matches what the copier expects (spec section 14.1):
      config/
        VivadoProject/          ← vivado_dir  (found by _find_vivado_dir)
          my_proj/              ← project_dir (found by _resolve_vivado_project_root)
            my_proj.srcs/
            my_proj.sim/
            my_proj.runs/
            build.tcl
    """
    vivado_wrapper = db / "config" / "VivadoProject"
    proj = vivado_wrapper / project_name                 # project_dir

    (proj / f"{project_name}.srcs" / "sources_1" / "new").mkdir(parents=True)
    (proj / f"{project_name}.srcs" / "sim_1"     / "new").mkdir(parents=True)
    (proj / f"{project_name}.srcs" / "constrs_1").mkdir(parents=True)
    sim_xsim = proj / f"{project_name}.sim" / "sim_1" / "behav" / "xsim"
    sim_xsim.mkdir(parents=True)
    (proj / f"{project_name}.runs" / "synth_1").mkdir(parents=True)
    (proj / f"{project_name}.runs" / "impl_1").mkdir(parents=True)

    # Sample source files
    (proj / f"{project_name}.srcs" / "sources_1" / "new" / "top.sv").write_text("module top;endmodule")
    (proj / f"{project_name}.srcs" / "sim_1"     / "new" / "top_tb.sv").write_text("module top_tb;endmodule")
    (proj / f"{project_name}.srcs" / "constrs_1" / "pins.xdc").write_text("# constraints")
    (proj / "build.tcl").write_text("# tcl script")

    # Sample artifact files
    (sim_xsim / "xsim.log").write_text("Simulation log")
    (sim_xsim / "dump.wdb").write_text("Waveform data")
    (proj / f"{project_name}.runs" / "synth_1" / "synth.log").write_text("Synth log")
    (proj / f"{project_name}.runs" / "synth_1" / "util.rpt").write_text("Util report")
    (proj / f"{project_name}.runs" / "impl_1"  / "impl.log").write_text("Impl log")
    (proj / f"{project_name}.runs" / "impl_1"  / "timing.rpt").write_text("Timing report")

    return vivado_wrapper


# ─────────────────────────────────────────────────────────────────────────
# tile_id tests
# ─────────────────────────────────────────────────────────────────────────

def test_tile_id_format():
    import sys; sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.tile_id import generate_tile_id
    tid = generate_tile_id("MST130-01", "01", "02", 1, date(2026, 3, 6))
    assert tid == "MST130-01-26030600010102"


def test_tile_id_tile_number_padding():
    from core.tile_id import generate_tile_id
    tid = generate_tile_id("X", "00", "00", 42, date(2026, 1, 1))
    assert "0042" in tid


# ─────────────────────────────────────────────────────────────────────────
# run_id tests
# ─────────────────────────────────────────────────────────────────────────

def test_run_id_empty_dir(tmp_path):
    from core.run_id import next_run_id
    runs = tmp_path / "runs"
    runs.mkdir()
    assert next_run_id(runs) == "run-001"


def test_run_id_after_existing(tmp_path):
    from core.run_id import next_run_id
    runs = tmp_path / "runs"
    runs.mkdir()
    (runs / "run-001").mkdir()
    (runs / "run-002").mkdir()
    assert next_run_id(runs) == "run-003"


def test_run_id_ignores_invalid_folders(tmp_path):
    from core.run_id import next_run_id
    runs = tmp_path / "runs"
    runs.mkdir()
    (runs / "run-001").mkdir()
    (runs / "temp").mkdir()          # invalid
    (runs / "run-abc").mkdir()       # invalid
    assert next_run_id(runs) == "run-002"


# ─────────────────────────────────────────────────────────────────────────
# create-tile tests
# ─────────────────────────────────────────────────────────────────────────

def test_create_tile_basic(tmp_path):
    import sys; sys.path.insert(0, str(Path(__file__).parent.parent))
    db = make_db(tmp_path)
    write_tile_config(db)

    from commands.create_tile import run_create_tile
    run_create_tile(db)

    tiles = list((db / "tiles").iterdir())
    assert len(tiles) == 1
    tile_root = tiles[0]
    assert (tile_root / "README.md").exists()
    assert (tile_root / "works").is_dir()
    assert (tile_root / "runs").is_dir()


def test_create_tile_tile_index_row(tmp_path):
    db = make_db(tmp_path)
    write_tile_config(db)

    from commands.create_tile import run_create_tile
    run_create_tile(db)

    content = (db / "tile_index.csv").read_text(encoding="utf-8")
    lines = content.strip().splitlines()
    assert lines[0] == "tile_number,tile_id,tile_name,tile_author"
    assert len(lines) == 2
    row = lines[1].split(",")
    assert row[0] == "0001"
    assert row[2] == "Test Tile"


def test_create_tile_readme_content(tmp_path):
    db = make_db(tmp_path)
    write_tile_config(db)

    from commands.create_tile import run_create_tile
    run_create_tile(db)

    tiles = list((db / "tiles").iterdir())
    readme = (tiles[0] / "README.md").read_text(encoding="utf-8")
    assert "Test Tile" in readme
    assert "port_a" in readme


def test_create_tile_invalid_id_version(tmp_path):
    from core.validator import AutoDocError
    db = make_db(tmp_path)
    write_tile_config(db, overrides={"id_version": "1"})  # not 2 digits

    from commands.create_tile import run_create_tile
    with raises(AutoDocError, match="id_version"):
        run_create_tile(db)


def test_create_tile_invalid_id_revision(tmp_path):
    from core.validator import AutoDocError
    db = make_db(tmp_path)
    write_tile_config(db, overrides={"id_revision": "abc"})

    from commands.create_tile import run_create_tile
    with raises(AutoDocError, match="id_revision"):
        run_create_tile(db)


def test_create_tile_consecutive_numbering(tmp_path):
    db = make_db(tmp_path)
    write_tile_config(db)

    from commands.create_tile import run_create_tile

    # Create two tiles (different id_prefix to avoid same-second collision)
    run_create_tile(db)
    write_tile_config(db, overrides={"id_prefix": "TST2", "id_version": "02"})
    run_create_tile(db)

    content = (db / "tile_index.csv").read_text(encoding="utf-8")
    lines = content.strip().splitlines()
    assert len(lines) == 3  # header + 2 rows
    assert lines[1].split(",")[0] == "0001"
    assert lines[2].split(",")[0] == "0002"


# ─────────────────────────────────────────────────────────────────────────
# create-run tests
# ─────────────────────────────────────────────────────────────────────────

def _setup_tile(tmp_path) -> tuple[Path, str]:
    """Helper: create db + tile. Vivado project and run_config are NOT created here."""
    db = make_db(tmp_path)
    write_tile_config(db)

    from commands.create_tile import run_create_tile
    run_create_tile(db)

    tiles = list((db / "tiles").iterdir())
    return db, tiles[0].name


def test_create_run_structure(tmp_path):
    db, tile_id = _setup_tile(tmp_path)
    write_run_config(db)
    make_vivado_project(db)

    from commands.create_run import run_create_run
    run_create_run(db, tile_id)

    run_root = db / "tiles" / tile_id / "runs" / "run-001"
    assert run_root.is_dir()
    assert (run_root / "manifest.yaml").exists()
    assert (run_root / "notes.md").exists()
    # run_config.yaml is NOT stored in the run folder (by design)
    assert not (run_root / "run_config.yaml").exists()
    for subdir in (
        "src/rtl", "src/tb", "src/constraints", "src/scripts",
        "out/sim/logs", "out/sim/waves",
        "out/synth/logs", "out/synth/reports",
        "out/impl/logs", "out/impl/reports",
    ):
        assert (run_root / subdir).is_dir(), f"Missing: {subdir}"


def test_create_run_files_copied(tmp_path):
    db, tile_id = _setup_tile(tmp_path)
    write_run_config(db)
    make_vivado_project(db)

    from commands.create_run import run_create_run
    run_create_run(db, tile_id)

    run_root = db / "tiles" / tile_id / "runs" / "run-001"
    assert (run_root / "src" / "rtl" / "top.sv").exists()
    assert (run_root / "src" / "tb"  / "top_tb.sv").exists()
    assert (run_root / "src" / "constraints" / "pins.xdc").exists()
    assert (run_root / "src" / "scripts" / "build.tcl").exists()
    assert (run_root / "out" / "sim" / "logs"   / "xsim.log").exists()
    assert (run_root / "out" / "sim" / "waves"  / "dump.wdb").exists()
    assert (run_root / "out" / "synth" / "logs" / "synth.log").exists()
    assert (run_root / "out" / "synth" / "reports" / "util.rpt").exists()
    assert (run_root / "out" / "impl" / "logs"  / "impl.log").exists()
    assert (run_root / "out" / "impl" / "reports" / "timing.rpt").exists()


def test_create_run_manifest_paths_relative(tmp_path):
    """Section 15 — all paths in manifest must start with tiles/."""
    db, tile_id = _setup_tile(tmp_path)
    write_run_config(db)
    make_vivado_project(db)

    from commands.create_run import run_create_run
    run_create_run(db, tile_id)

    manifest_path = db / "tiles" / tile_id / "runs" / "run-001" / "manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))

    for cat in ("rtl", "tb", "constraints", "scripts"):
        for p in manifest["sources"][cat]:
            assert p.startswith("tiles/"), f"Path not relative to tiles/: {p}"
    for key in ("sim_log", "wave"):
        for p in manifest["artifacts"][key]:
            assert p.startswith("tiles/"), f"Path not relative to tiles/: {p}"


def test_create_run_records_csv_row(tmp_path):
    db, tile_id = _setup_tile(tmp_path)
    write_run_config(db)
    make_vivado_project(db)

    from commands.create_run import run_create_run
    run_create_run(db, tile_id)

    content = (db / "records.csv").read_text(encoding="utf-8")
    lines = content.strip().splitlines()
    expected_header = (
        "Tile_ID,Run_ID,Date,Author,Objective,Status,"
        "Main_Change,Run_Path,Vivado_Version,Result_Summary,Tags"
    )
    assert lines[0] == expected_header
    assert len(lines) == 2
    row = dict(zip(lines[0].split(","), lines[1].split(",")))
    assert row["Tile_ID"] == tile_id
    assert row["Run_ID"] == "run-001"
    assert row["Run_Path"] == f"tiles/{tile_id}/runs/run-001"
    assert row["Status"] == "PASS"


def test_create_run_works_updated(tmp_path):
    db, tile_id = _setup_tile(tmp_path)
    write_run_config(db)
    make_vivado_project(db)

    from commands.create_run import run_create_run
    run_create_run(db, tile_id)

    works_root = db / "tiles" / tile_id / "works"
    assert (works_root / "rtl"  / "top.sv").exists()
    assert (works_root / "tb"   / "top_tb.sv").exists()
    assert (works_root / "constraints" / "pins.xdc").exists()
    assert (works_root / "scripts" / "build.tcl").exists()


def test_create_run_invalid_status(tmp_path):
    from core.validator import AutoDocError
    db, tile_id = _setup_tile(tmp_path)
    write_run_config(db, overrides={"status": "INVALID"})
    make_vivado_project(db)

    from commands.create_run import run_create_run
    with raises(AutoDocError, match="status"):
        run_create_run(db, tile_id)


def test_create_run_tile_not_found(tmp_path):
    from core.validator import AutoDocError
    db = make_db(tmp_path)
    write_tile_config(db)
    write_run_config(db)
    make_vivado_project(db)

    from commands.create_run import run_create_run
    with raises(AutoDocError, match="does not exist"):
        run_create_run(db, "NONEXISTENT-TILE-ID")


def test_create_run_consecutive(tmp_path):
    db, tile_id = _setup_tile(tmp_path)
    write_run_config(db)
    make_vivado_project(db)

    from commands.create_run import run_create_run
    run_create_run(db, tile_id)
    run_create_run(db, tile_id)
    run_create_run(db, tile_id)

    runs = list((db / "tiles" / tile_id / "runs").iterdir())
    names = sorted(r.name for r in runs if r.is_dir())
    assert names == ["run-001", "run-002", "run-003"]


# ─────────────────────────────────────────────────────────────────────────
# init_db tests
# ─────────────────────────────────────────────────────────────────────────

def test_init_db_creates_structure(tmp_path):
    import sys; sys.path.insert(0, str(Path(__file__).parent.parent))
    from commands.init_db import run_init_db

    db = tmp_path / "database"
    run_init_db(db)

    assert (db / "tiles").is_dir()
    assert (db / "config").is_dir()
    assert (db / "tile_index.csv").exists()
    assert (db / "records.csv").exists()
    assert (db / "config" / "tile_config.yaml").exists()
    assert (db / "config" / "run_config.yaml").exists()
    assert (db / "tiles" / ".gitkeep").exists()


def test_init_db_yaml_templates_not_empty(tmp_path):
    from commands.init_db import run_init_db

    db = tmp_path / "database"
    run_init_db(db)

    tile_cfg = (db / "config" / "tile_config.yaml").read_text(encoding="utf-8")
    run_cfg  = (db / "config" / "run_config.yaml").read_text(encoding="utf-8")

    assert "id_prefix" in tile_cfg
    assert "id_version" in tile_cfg
    assert "description" in tile_cfg
    assert "run_author" in run_cfg
    assert "constraints_used" in run_cfg
    assert "PASS | FAIL | WIP | EXCLUDE" in run_cfg


def test_init_db_csv_files_empty(tmp_path):
    from commands.init_db import run_init_db

    db = tmp_path / "database"
    run_init_db(db)

    assert (db / "tile_index.csv").read_text(encoding="utf-8") == ""
    assert (db / "records.csv").read_text(encoding="utf-8") == ""


def test_init_db_existing_dir_raises(tmp_path):
    from commands.init_db import run_init_db
    from core.validator import AutoDocError

    db = tmp_path / "database"
    db.mkdir()
    with raises(AutoDocError, match="already exists"):
        run_init_db(db, force=False)


def test_init_db_force_skips_existing(tmp_path):
    from commands.init_db import run_init_db

    db = tmp_path / "database"
    run_init_db(db)

    # Modify tile_config.yaml
    tile_cfg_path = db / "config" / "tile_config.yaml"
    tile_cfg_path.write_text("id_prefix: MODIFIED", encoding="utf-8")

    # Run init again with force — should not overwrite
    run_init_db(db, force=True)
    assert "MODIFIED" in tile_cfg_path.read_text(encoding="utf-8")


def test_init_db_then_create_tile(tmp_path):
    """Full flow: init → fill config → create-tile."""
    from commands.init_db import run_init_db
    from commands.create_tile import run_create_tile

    db = tmp_path / "database"
    run_init_db(db)

    # Overwrite template with real data
    write_tile_config(db)

    run_create_tile(db)

    tiles = list((db / "tiles").iterdir())
    # filter out .gitkeep
    tile_dirs = [t for t in tiles if t.is_dir()]
    assert len(tile_dirs) == 1
    assert (tile_dirs[0] / "README.md").exists()

def test_bad_tile_index_header(tmp_path):
    from core.validator import AutoDocError, validate_tile_index_csv
    f = tmp_path / "tile_index.csv"
    f.write_text("wrong,header,here\n0001,X,Y,Z\n", encoding="utf-8")
    with raises(AutoDocError, match="Invalid CSV header"):
        validate_tile_index_csv(f)


def test_bad_records_header(tmp_path):
    from core.validator import AutoDocError, validate_records_csv
    f = tmp_path / "records.csv"
    f.write_text("col1,col2\nval1,val2\n", encoding="utf-8")
    with raises(AutoDocError, match="Invalid CSV header"):
        validate_records_csv(f)


def test_empty_csv_header_skipped(tmp_path):
    from core.validator import validate_tile_index_csv, validate_records_csv
    ti = tmp_path / "tile_index.csv"
    rc = tmp_path / "records.csv"
    ti.write_text("", encoding="utf-8")
    rc.write_text("", encoding="utf-8")
    # Must not raise
    validate_tile_index_csv(ti)
    validate_records_csv(rc)


# ─────────────────────────────────────────────────────────────────────────
# Copy collision test (section 14.3)
# ─────────────────────────────────────────────────────────────────────────

def test_copy_flat_collision(tmp_path):
    from core.copier import _copy_flat

    origin = tmp_path / "origin"
    (origin / "sub1").mkdir(parents=True)
    (origin / "sub2").mkdir(parents=True)
    (origin / "sub1" / "file.sv").write_text("v1")
    (origin / "sub2" / "file.sv").write_text("v2")

    dest = tmp_path / "dest"
    copied = _copy_flat(origin, dest, {".sv"})

    assert len(copied) == 2
    names = {p.name for p in copied}
    assert "file.sv" in names
    assert "file_1.sv" in names


def test_copy_missing_origin_returns_empty(tmp_path):
    from core.copier import _copy_flat
    result = _copy_flat(tmp_path / "nonexistent", tmp_path / "dest", {".sv"})
    assert result == []
