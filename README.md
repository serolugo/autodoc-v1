# AutoDoc V1

A command-line tool for documenting and tracking Vivado-based tile development. AutoDoc captures a structured snapshot of every work session — source files, logs, reports, and waveforms — and maintains a traceable history with auto-generated documentation.

---

## Requirements

- Python 3.10+
- PyYAML

```bash
pip install PyYAML
```

---

## Installation

```bash
[git clone https://github.com/serolugo/autodoc-v1.git]
cd autodoc
pip install PyYAML
python tests/runner.py  # verify: 30 passed, 0 failed
```

---

## Commands

### `init`
Creates the full database skeleton with config templates ready to fill.

```bash
python cli.py --db "path/to/database" init
```

| Flag | Description |
|---|---|
| *(none)* | Creates from scratch. Fails if folder already exists. |
| `--force` | Runs inside an existing folder without overwriting files. |

**Output:**
```
database/
├── tile_index.csv
├── records.csv
├── tiles/
└── config/
    ├── tile_config.yaml
    └── run_config.yaml
```

---

### `create-tile`
Registers a new tile and generates its base documentation.

```bash
python cli.py --db "path/to/database" create-tile
```

**Input:** `database/config/tile_config.yaml`

```yaml
id_prefix: "MST130-01"   # tile ID prefix
id_version: "01"          # 2 digits
id_revision: "01"         # 2 digits
tile_name: "My Tile"
tile_author: "Author Name"
description: |
  What this tile does.
ports: |
  port_a [3:0] -> Input
  port_b [3:0] -> Output
usage_guide: |
  How to use this tile.
tb_description: |
  What the testbench verifies.
```

**Output:**
```
database/tiles/<tile_id>/
├── README.md
├── works/
│   ├── rtl/
│   ├── tb/
│   ├── constraints/
│   └── scripts/
└── runs/
```

Prints the generated `tile_id` — save it for `create-run`.

---

### `create-run`
Captures a full snapshot of the current Vivado project into a new run folder.

```bash
python cli.py --db "path/to/database" create-run --tile <tile_id>
```

**Inputs:**

`database/config/run_config.yaml`

```yaml
run_author: "Author Name"
objective: "What this run tests"
status: "PASS"              # PASS | FAIL | WIP | EXCLUDE
vivado_version: "2023.2"
sim: "xsim"
top: "tb_module_name"
seed: "1"
sim_time: "1000ns"
constraints_used: false
tags: "smoke baseline"
summary: |
  Run result summary.
key_warnings: |
  Notable warnings.
key_errors: |
  Notable errors.
main_change: |
  What changed in this run.
notes: |
  Additional notes.
```

`database/config/<VivadoProject>/` — your Vivado project folder pasted here.

**Output:**
```
database/tiles/<tile_id>/runs/run-001/
├── manifest.yaml       ← structured run record
├── notes.md            ← run notes
├── src/
│   ├── rtl/            ← .v .sv source files
│   ├── tb/             ← testbench files
│   ├── constraints/    ← .xdc files
│   └── scripts/        ← .tcl .py scripts
└── out/
    ├── sim/
    │   ├── logs/       ← .log files
    │   └── waves/      ← .wdb waveform files
    ├── synth/
    │   ├── logs/
    │   └── reports/    ← .rpt files
    └── impl/
        ├── logs/
        └── reports/    ← .rpt files
```

Also updates:
- `database/tiles/<tile_id>/README.md` — regenerated
- `database/tiles/<tile_id>/works/` — updated with latest sources
- `database/records.csv` — new row appended

---

## Tile ID format

```
<id_prefix>-<YYMMDD><tile_number:04h><id_version><id_revision>
```

Example: `MST130-01-26031500010101`

---

## Files copied from Vivado

| Category | Source | Extensions |
|---|---|---|
| rtl | `<proj>.srcs/sources_1/new/` | `.v` `.sv` |
| tb | `<proj>.srcs/sim_1/new/` | `.v` `.sv` |
| constraints | `<proj>.srcs/constrs_1/` | `.xdc` |
| scripts | project root | `.tcl` `.py` |
| sim logs | `<proj>.sim/sim_1/behav/xsim/` | `.log` |
| waves | `<proj>.sim/sim_1/behav/xsim/` | `.wdb` |
| synth logs/reports | `<proj>.runs/synth_1/` | `.log` `.rpt` |
| impl logs/reports | `<proj>.runs/impl_1/` | `.log` `.rpt` |

Missing categories do not stop the run — they are recorded as empty lists in `manifest.yaml`.

---

## Project structure

```
autodoc/
├── cli.py
├── requirements.txt
├── commands/
│   ├── init_db.py
│   ├── create_tile.py
│   └── create_run.py
├── core/
│   ├── validator.py
│   ├── tile_id.py
│   ├── run_id.py
│   ├── csv_store.py
│   └── copier.py
├── generators/
│   ├── readme.py
│   ├── notes.py
│   └── manifest.py
├── models/
│   ├── tile_config.py
│   └── run_config.py
├── tests/
│   ├── runner.py
│   └── test_autodoc.py
└── docs/
    ├── MANUAL.md
    ├── TECHNICAL.md
    ├── QUICKREF.md
    └── METHODS.md
```

---

## Running the tests

```bash
python tests/runner.py
# Results: 30 passed, 0 failed — ALL TESTS PASSED
```
