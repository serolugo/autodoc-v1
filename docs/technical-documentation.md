# AutoDoc V1 — Technical Documentation

## Architecture overview

AutoDoc follows a layered architecture. Each layer has a single responsibility and depends only on the layers below it.

```
cli.py
   ↓
commands/          ← orchestration (create-tile, create-run flows)
   ↓
core/              ← logic (IDs, CSV, copy, validation)
generators/        ← file rendering (README, notes, manifest)
models/            ← data structures (TileConfig, RunConfig)
```

---

## Project structure

```
Autodoc/
├── cli.py                  ← entry point, argument parsing
├── requirements.txt        ← PyYAML
├── commands/
│   ├── init_db.py          ← init flow (database skeleton creation)
│   ├── create_tile.py      ← create-tile flow (spec section 10)
│   └── create_run.py       ← create-run flow (spec section 11)
├── core/
│   ├── validator.py        ← validation rules (spec section 16)
│   ├── tile_id.py          ← tile ID generation (spec section 5)
│   ├── run_id.py           ← run folder detection (spec section 6)
│   ├── csv_store.py        ← CSV read/write (spec section 7)
│   └── copier.py           ← file copy logic (spec section 14)
├── generators/
│   ├── readme.py           ← README.md template
│   ├── notes.py            ← notes.md template
│   └── manifest.py         ← manifest.yaml serializer
├── models/
│   ├── tile_config.py      ← TileConfig dataclass
│   └── run_config.py       ← RunConfig dataclass
└── tests/
    ├── runner.py           ← standalone test runner
    └── test_autodoc.py     ← 24 integration tests
```

---

## cli.py

Entry point for all commands. Uses `argparse` with subcommands.

**Arguments:**

| Argument | Description |
|---|---|
| `--db PATH` | Path to the `database/` root directory. Must be passed before the subcommand. Default: `./database` |
| `create-tile` | Subcommand: create a tile base structure |
| `create-run --tile TILE_ID` | Subcommand: create a documented run for an existing tile |

**Design notes:**
- Imports commands lazily inside each handler to keep startup fast
- All errors from `AutoDocError` are caught here and printed cleanly before exiting with code 1

---

## commands/init_db.py

Creates the full `database/` skeleton in a single command.

**When to use:** once per project, before any other command.

**What it creates:**

| Path | Description |
|---|---|
| `database/tiles/` | Empty directory with `.gitkeep` |
| `database/config/` | Empty directory |
| `database/config/tile_config.yaml` | Template with all fields and comments |
| `database/config/run_config.yaml` | Template with all fields and comments |
| `database/tile_index.csv` | Empty file |
| `database/records.csv` | Empty file |

**Key function:** `run_init_db(db_root: Path, force: bool = False)`

**Behavior:**
- If `db_root` does not exist it is created automatically
- If `db_root` already exists and `force=False` → raises `AutoDocError`
- If `force=True` → skips any files that already exist without overwriting them. This makes `init --force` safe to run on an existing database.

**Templates:** `_TILE_CONFIG_TEMPLATE` and `_RUN_CONFIG_TEMPLATE` are module-level string constants inside `init_db.py`. Editing them changes what gets written on every new `init`.

---

## commands/create_tile.py

Orchestrates the full `create-tile` flow in 8 steps:

1. Validate required paths (`validate_create_tile_structure`)
2. Validate CSV header if non-empty
3. Read and parse `tile_config.yaml`
4. Validate `id_version` and `id_revision` are exactly 2 digits
5. Obtain next `tile_number` from `tile_index.csv`
6. Generate `tile_id`
7. Create `database/tiles/<tile_id>/` with `README.md`, `works/`, and `runs/`
8. Append row to `tile_index.csv`

**Key function:** `run_create_tile(db_root: Path)`

---

## commands/create_run.py

Orchestrates the full `create-run` flow in 13 steps:

1. Validate required paths (`validate_create_run_structure`)
2. Validate CSV headers
3. Verify target tile exists
4. Read `tile_config.yaml` and `run_config.yaml`
5. Validate `status` value
6. Determine next run ID by scanning existing run folders
7. Create run folder and full internal structure
8. Copy source files from Vivado project
9. Copy generated artifacts from Vivado project
10. Generate `manifest.yaml`
11. Generate `notes.md`
12. Regenerate tile `README.md`
13. Update `works/` with latest sources
14. Append row to `records.csv`

**Key function:** `run_create_run(db_root: Path, tile_id: str)`

**Helper functions:**
- `_gitkeep(directory)` — places `.gitkeep` in a directory
- `_create_run_structure(run_root)` — creates all run subdirectories
- `_update_works(tile_root, run_src)` — clears and repopulates `works/`
- `_find_vivado_dir(config_dir)` — returns the first subdirectory inside `config/`

---

## core/validator.py

Defines `AutoDocError` and all validation functions.

| Function | Validates |
|---|---|
| `validate_create_tile_structure(db_root)` | Paths required by `create-tile`: `config/`, `tiles/`, `tile_config.yaml`, `tile_index.csv`, `records.csv` |
| `validate_create_run_structure(db_root)` | All of the above plus `run_config.yaml` and at least one subdirectory in `config/` |
| `validate_csv_header(path, expected, label)` | Skips if file is empty; raises `AutoDocError` if header does not match exactly |
| `validate_tile_config_fields(id_version, id_revision)` | Both must match `\d{2}` |
| `validate_run_status(status)` | Must be one of `PASS`, `FAIL`, `WIP`, `EXCLUDE` |
| `validate_tile_exists(tiles_root, tile_id)` | Tile directory must exist under `tiles/` |

**Design note:** `validate_create_tile_structure` and `validate_create_run_structure` are intentionally separate. `create-tile` does not require `run_config.yaml` or a Vivado project — those are only needed by `create-run`.

---

## core/tile_id.py

Generates the `tile_id` string from its components.

**Format:** `<id_prefix>-<YYMMDD><tile_number:04d><id_version><id_revision>`

**Function:** `generate_tile_id(id_prefix, id_version, id_revision, tile_number, creation_date)`

- `creation_date` defaults to `date.today()`
- `tile_number` is zero-padded to 4 digits

---

## core/run_id.py

Detects and generates run folder names.

**Functions:**

| Function | Description |
|---|---|
| `next_run_id(runs_dir)` | Returns the next run name (e.g. `run-003`). Returns `run-001` if no valid runs exist |
| `list_valid_run_folders(runs_dir)` | Returns all folders matching `run-\d{3}`, sorted ascending |
| `latest_run_folder(runs_dir)` | Returns the most recent valid run folder or `None` |

**Design note:** only folders matching the exact pattern `run-\d{3}` are considered valid. Any other folder name is silently ignored.

---

## core/csv_store.py

Handles all CSV read and write operations.

**tile_index.csv functions:**

| Function | Description |
|---|---|
| `read_tile_index(path)` | Returns all rows as a list of dicts, or `[]` if empty |
| `next_tile_number(path)` | Returns `max(tile_number) + 1`, or `1` if empty |
| `append_tile_index_row(path, ...)` | Writes header first if file is empty, then appends the row |

**records.csv functions:**

| Function | Description |
|---|---|
| `append_records_row(path, ...)` | Writes header first if file is empty, then appends the row |

**Design note:** the header is written automatically the first time a row is appended to an empty file (spec section 16.4). Callers never need to initialize the files manually.

---

## core/copier.py

Handles all file discovery and copying from the Vivado project.

**Project detection (`_resolve_vivado_project_root`):**

Supports two layouts automatically:

- **Layout A** — project folder is directly the folder inside `config/` (real Vivado projects: `config/tile_16bit_adder/tile_16bit_adder.srcs/...`)
- **Layout B** — project folder is a subdirectory inside a wrapper folder (test layout: `config/VivadoProject/my_proj/my_proj.srcs/...`)

Detection logic: if a `.srcs` folder named `<dir_name>.srcs` exists directly inside `vivado_dir`, use Layout A. Otherwise fall back to Layout B.

**Origin paths per category (relative to project dir):**

| Category | Origin path |
|---|---|
| rtl | `<proj>.srcs/sources_1/new/` |
| tb | `<proj>.srcs/sim_1/new/` |
| constraints | `<proj>.srcs/constrs_1/` |
| scripts | project root |
| sim logs/waves | `<proj>.sim/sim_1/behav/xsim/` |
| synth logs/reports | `<proj>.runs/synth_1/` |
| impl logs/reports | `<proj>.runs/impl_1/` |

**Copy behavior:**
- Recursive search in origin directory
- Flat copy in destination (no subdirectory preservation)
- Name collisions resolved with `_1`, `_2` suffixes
- Missing origin directories return `[]` without stopping the run

**Public functions:**

| Function | Description |
|---|---|
| `copy_sources(vivado_dir, run_src)` | Copies rtl, tb, constraints, scripts |
| `copy_artifacts(vivado_dir, run_out)` | Copies sim logs, waves, synth/impl logs and reports |

---

## generators/readme.py

Renders `README.md` from a string template using `str.format()`.

**Template fields:** `tile_id`, `tile_name`, `description`, `ports`, `usage_guide`, `tb_description`

**Functions:**
- `render_readme(tile_id, cfg)` → returns rendered string
- `write_readme(tile_root, tile_id, cfg)` → writes file to disk

Called by `create-tile` on creation and by `create-run` on every run to keep it up to date.

---

## generators/notes.py

Renders `notes.md` from a string template.

**Template fields:** `tile_id`, `tile_name`, `notes`

**Functions:**
- `render_notes(tile_id, tile_cfg, run_cfg)` → returns rendered string
- `write_notes(run_root, tile_id, tile_cfg, run_cfg)` → writes file to disk

---

## generators/manifest.py

Builds and serializes `manifest.yaml` using a custom writer instead of PyYAML's default dumper. This allows blank lines to be inserted between logical sections for readability.

**Blank lines are placed after:** `author`, `status`, `simulator`, `constraints_used`, `scripts`, `wave`.

**Functions:**
- `build_manifest(...)` → returns the manifest as a Python dict (also used by tests)
- `write_manifest(run_root, manifest)` → serializes and writes the file
- `_render_manifest(manifest)` → internal serializer that produces the formatted YAML string

**All paths stored in `sources` and `artifacts` are relative to `tiles/`** (spec section 15).

---

## models/tile_config.py

Dataclass `TileConfig` with fields:

| Field | Type | Source |
|---|---|---|
| `id_prefix` | str | tile_config.yaml |
| `id_version` | str | tile_config.yaml |
| `id_revision` | str | tile_config.yaml |
| `tile_name` | str | tile_config.yaml |
| `tile_author` | str | tile_config.yaml |
| `description` | str | tile_config.yaml |
| `ports` | str | tile_config.yaml |
| `usage_guide` | str | tile_config.yaml |
| `tb_description` | str | tile_config.yaml |

`from_dict(data)` — parses a raw YAML dict. Missing fields default to `""`.

---

## models/run_config.py

Dataclass `RunConfig` with fields:

| Field | Type | Source |
|---|---|---|
| `run_author` | str | run_config.yaml |
| `objective` | str | run_config.yaml |
| `status` | str | run_config.yaml |
| `vivado_version` | str | run_config.yaml |
| `sim` | str | run_config.yaml |
| `top` | str | run_config.yaml |
| `seed` | str | run_config.yaml |
| `sim_time` | str | run_config.yaml |
| `constraints_used` | bool | run_config.yaml |
| `tags` | str | run_config.yaml |
| `summary` | str | run_config.yaml |
| `key_warnings` | str | run_config.yaml |
| `key_errors` | str | run_config.yaml |
| `main_change` | str | run_config.yaml |
| `notes` | str | run_config.yaml |

`from_dict(data)` — parses a raw YAML dict. `constraints_used` accepts `true/false`, `yes/no`, or `1/0`.

---

## tests/runner.py

Standalone test runner that does not require pytest. Runs all 30 tests using Python's `tempfile` module to create and destroy isolated directories for each test.

**Usage:**
```powershell
python tests\runner.py
```

Each test that needs a filesystem gets a fresh temporary directory passed as `tmp_path`. The directory is deleted automatically after each test regardless of pass or fail.

---

## tests/test_autodoc.py

Contains 30 integration tests organized in 6 groups.

### Group 1 — tile_id (2 tests)

| Test | What it verifies |
|---|---|
| `test_tile_id_format` | Generated ID matches `MST130-01-26030600010102` exactly |
| `test_tile_id_tile_number_padding` | tile_number is zero-padded to 4 digits |

### Group 2 — run_id (3 tests)

| Test | What it verifies |
|---|---|
| `test_run_id_empty_dir` | First run is `run-001` when no runs exist |
| `test_run_id_after_existing` | Next run after `run-001` and `run-002` is `run-003` |
| `test_run_id_ignores_invalid_folders` | Folders like `temp/` or `run-abc/` are ignored |

### Group 3 — init_db (6 tests)

| Test | What it verifies |
|---|---|
| `test_init_db_creates_structure` | All folders, CSV files and YAML templates are created |
| `test_init_db_yaml_templates_not_empty` | Templates contain the expected field names and comments |
| `test_init_db_csv_files_empty` | CSV files are created empty |
| `test_init_db_existing_dir_raises` | Raises error if directory exists and `force=False` |
| `test_init_db_force_skips_existing` | `force=True` does not overwrite existing files |
| `test_init_db_then_create_tile` | Full flow: `init` → fill config → `create-tile` works end to end |

### Group 4 — create-tile (6 tests)

| Test | What it verifies |
|---|---|
| `test_create_tile_basic` | `README.md`, `works/`, and `runs/` are created |
| `test_create_tile_tile_index_row` | CSV header and row written correctly |
| `test_create_tile_readme_content` | README contains tile name and port data |
| `test_create_tile_invalid_id_version` | Raises error if `id_version` is not 2 digits |
| `test_create_tile_invalid_id_revision` | Raises error if `id_revision` is not 2 digits |
| `test_create_tile_consecutive_numbering` | Second tile gets `tile_number = 0002` |

### Group 5 — create-run (8 tests)

| Test | What it verifies |
|---|---|
| `test_create_run_structure` | All subdirectories created, `run_config.yaml` not stored in run |
| `test_create_run_files_copied` | Source and artifact files copied to correct locations |
| `test_create_run_manifest_paths_relative` | All paths in manifest start with `tiles/` |
| `test_create_run_records_csv_row` | CSV header, tile_id, run_id, run_path, status correct |
| `test_create_run_works_updated` | `works/` contains files from the latest run |
| `test_create_run_invalid_status` | Raises error for status outside allowed values |
| `test_create_run_tile_not_found` | Raises error if tile directory does not exist |
| `test_create_run_consecutive` | Three consecutive runs produce `run-001`, `run-002`, `run-003` |

### Group 6 — validation and copy (5 tests)

| Test | What it verifies |
|---|---|
| `test_bad_tile_index_header` | Raises error on wrong CSV header in `tile_index.csv` |
| `test_bad_records_header` | Raises error on wrong CSV header in `records.csv` |
| `test_empty_csv_header_skipped` | Empty CSV files pass validation without error |
| `test_copy_flat_collision` | Two files with same name produce `file.sv` and `file_1.sv` |
| `test_copy_missing_origin_returns_empty` | Missing Vivado directory returns `[]` without error |

---

## Error handling

All hard errors raise `AutoDocError` which is a subclass of `Exception`. The CLI catches it and prints a clean message:

```
[ERROR] Invalid status 'INVALID': must be one of ['EXCLUDE', 'FAIL', 'PASS', 'WIP'].
```

Soft failures (missing copy categories, empty YAML fields) are handled silently and represented as empty values in the output files.
