# AutoDoc V1 — User Manual

## What is AutoDoc?

AutoDoc is a command-line tool that creates and maintains structured documentation for Vivado-based tile development. It captures a snapshot of your source files and generated artifacts each time you run it, keeping a traceable history of every documented run.

---

## Requirements

- Python 3.10 or higher
- PyYAML

Install the dependency with:

```bash
pip install PyYAML
```

---

## Project structure

```
Autodoc/                  ← AutoDoc code (do not modify)
database/
├── tile_index.csv        ← global tile registry (auto-managed)
├── records.csv           ← run history (auto-managed)
├── tiles/                ← all generated tile documentation
└── config/
    ├── tile_config.yaml  ← fill before create-tile
    ├── run_config.yaml   ← fill before create-run
    └── YourVivadoProject/← paste your Vivado project here
```

---

## Initial setup (one time only)

The fastest way to set up a new database is with the `init` command:

```powershell
cd "C:\path\to\Autodoc"
python cli.py --db "C:\path\to\database" init
```

This creates the full structure automatically:

```
database/
├── tile_index.csv        ← empty, ready to use
├── records.csv           ← empty, ready to use
├── tiles/                ← empty, tiles will be created here
└── config/
    ├── tile_config.yaml  ← template ready to fill
    └── run_config.yaml   ← template ready to fill
```

If the folder already exists and you want to initialize inside it without overwriting existing files:

```powershell
python cli.py --db "C:\path\to\database" init --force
```

After running `init`, the only thing left to do manually is:
1. Fill in `config\tile_config.yaml` with your tile data
2. Paste your Vivado project inside `config\`
3. Fill in `config\run_config.yaml` before each run

---

### Manual setup (alternative)

If you prefer to create the structure yourself without the `init` command:

**1. Create the folders and CSV files:**

```powershell
New-Item -ItemType Directory -Path "C:\path\to\database\config"
New-Item -ItemType Directory -Path "C:\path\to\database\tiles"
New-Item -ItemType File -Path "C:\path\to\database\tile_index.csv"
New-Item -ItemType File -Path "C:\path\to\database\records.csv"
```

**2. Create `tile_config.yaml` inside `database\config\`:**

```yaml
id_prefix: ""        # e.g. MST130-01
id_version: ""       # exactly 2 digits, e.g. 01
id_revision: ""      # exactly 2 digits, e.g. 01

tile_name: ""        # descriptive name
tile_author: ""      # author(s)

description: |
  

ports: |
  

usage_guide: |
  

tb_description: |
  
```

**3. Create `run_config.yaml` inside `database\config\`:**

```yaml
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
  
```

---

## Command: init

Creates the full `database/` skeleton from scratch with config templates ready to fill.

**When to use:** once, when starting a new project or setting up AutoDoc on a new machine.

```powershell
cd "C:\path\to\Autodoc"
python cli.py --db "C:\path\to\database" init
```

**Flags:**

| Flag | Description |
|---|---|
| *(none)* | Creates everything from scratch. Fails if the folder already exists. |
| `--force` | Works inside an existing folder. Skips files that already exist without overwriting them. |

**Output example:**

```
[init] Database root: C:\path\to\database
[init] Created tiles/
[init] Created config/
[init] Created config/tile_config.yaml
[init] Created config/run_config.yaml
[init] Created tile_index.csv
[init] Created records.csv

✓ Database initialized successfully.
  Path : C:\path\to\database

Next steps:
  1. Fill in config/tile_config.yaml
  2. Paste your Vivado project inside config/
  3. Run: python cli.py --db "C:\path\to\database" create-tile
```

---

## Command: create-tile

Creates the base folder structure for a new tile and registers it in `tile_index.csv`.

**When to use:** once per tile, before any runs.

**Steps:**
1. Fill in `database\config\tile_config.yaml` with your tile data
2. Run the command

```powershell
cd "C:\path\to\Autodoc"
python cli.py --db "C:\path\to\database" create-tile
```

**What it creates:**

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

**Output example:**

```
[create-tile] Created tile directory: ...tiles\MST130-01-26031500010101
[create-tile] README.md written.
[create-tile] works/ structure created.
[create-tile] runs/ directory created.
[create-tile] tile_index.csv updated.

✓ Tile created successfully.
  Tile ID  : MST130-01-26031500010101
  Name     : Logical Operators
  Author   : Salvador Martinez and Cesar Gomez
```

> **Save the Tile ID.** You will need it every time you run `create-run`.

---

## Command: create-run

Captures a full snapshot of your current Vivado project into a new run folder.

**When to use:** after every significant simulation or implementation you want to document.

**Steps:**
1. Paste your Vivado project folder inside `database\config\`
2. Fill in `database\config\run_config.yaml`
3. Run the command

```powershell
python cli.py --db "C:\path\to\database" create-run --tile <tile_id>
```

**Example:**

```powershell
python cli.py --db "C:\Residencia_lugo\Auto_doc_pruebas\database" create-run --tile MST130-01-26031500010101
```

**What it creates:**

```
database/tiles/<tile_id>/runs/run-001/
├── manifest.yaml         ← structured run record
├── notes.md              ← run notes
├── src/
│   ├── rtl/              ← .v and .sv source files
│   ├── tb/               ← testbench files
│   ├── constraints/      ← .xdc files
│   └── scripts/          ← .tcl and .py scripts
└── out/
    ├── sim/
    │   ├── logs/         ← .log files from xsim
    │   └── waves/        ← .wdb waveform files
    ├── synth/
    │   ├── logs/
    │   └── reports/      ← .rpt reports
    └── impl/
        ├── logs/
        └── reports/      ← .rpt reports
```

It also:
- Regenerates `README.md` for the tile
- Updates `works/` with the latest source snapshot
- Appends a row to `records.csv`

**Output example:**

```
[create-run] Starting run-001 for tile MST130-01-26031500010101
[create-run] src/rtl: 1 file(s) copied.
[create-run] src/tb: 2 file(s) copied.
[create-run] manifest.yaml generated.
[create-run] notes.md generated.
[create-run] README.md regenerated.
[create-run] works/ updated.
[create-run] records.csv updated.

✓ Run created successfully.
  Tile ID  : MST130-01-26031500010101
  Run ID   : run-001
  Status   : PASS
```

---

## Tile ID format

```
<id_prefix>-<YYMMDD><tile_number><id_version><id_revision>
```

Example: `MST130-01-26031500010101`

| Part | Value | Source |
|---|---|---|
| `MST130-01` | id_prefix | tile_config.yaml |
| `260315` | date (YYMMDD) | system |
| `0001` | tile number | auto-incremented |
| `01` | id_version | tile_config.yaml |
| `01` | id_revision | tile_config.yaml |

---

## Run numbering

Runs are numbered consecutively per tile: `run-001`, `run-002`, `run-003`, etc. The number is determined automatically by scanning existing run folders.

---

## Status values

| Value | Meaning |
|---|---|
| `PASS` | Run completed successfully |
| `FAIL` | Run produced errors |
| `WIP` | Work in progress |
| `EXCLUDE` | Run excluded from analysis |

---

## Vivado project placement

Place your Vivado project folder directly inside `database\config\`:

```
database\config\
├── tile_config.yaml
├── run_config.yaml
└── tile_16bit_adder\        ← your Vivado project folder
    ├── tile_16bit_adder.srcs\
    ├── tile_16bit_adder.sim\
    └── tile_16bit_adder.runs\
```

AutoDoc detects the project automatically regardless of its name.

---

## Files copied per category

| Category | Source in Vivado project | Extensions |
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

## Git integration

Every folder created by AutoDoc contains a `.gitkeep` file so git tracks empty directories automatically. No extra configuration needed.

---

## Running the tests

To verify the installation is correct:

```powershell
cd "C:\path\to\Autodoc"
python tests\runner.py
```

Expected output: `Results: 24 passed, 0 failed — ALL TESTS PASSED ✓`
