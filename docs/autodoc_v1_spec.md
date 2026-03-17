# AutoDoc V1 Specification

## 1. Purpose

AutoDoc is a documentation-oriented workflow inspired by run-based flows such as OpenLane, but adapted for documentation, traceability, and evidence capture of Vivado-based tile development.

Its purpose is to:

- create a base structure for a tile
- generate documented runs for an existing tile
- copy source files and generated artifacts from a Vivado project
- generate structured documentation files
- maintain run traceability through CSV indexes

---

## 2. Global Structure

```text
database/
├─ tile_index.csv
├─ records.csv
├─ tiles/
│  ├─ <tile_id>/
│  │  ├─ README.md
│  │  ├─ works/
│  │  └─ runs/
│  │     ├─ run-001/
│  │     │  ├─ run_config.yaml
│  │     │  ├─ manifest.yaml
│  │     │  ├─ notes.md
│  │     │  ├─ src/
│  │     │  │  ├─ rtl/
│  │     │  │  ├─ tb/
│  │     │  │  ├─ constraints/
│  │     │  │  └─ scripts/
│  │     │  └─ out/
│  │     │     ├─ sim/
│  │     │     │  ├─ logs/
│  │     │     │  └─ waves/
│  │     │     ├─ synth/
│  │     │     │  ├─ logs/
│  │     │     │  └─ reports/
│  │     │     └─ impl/
│  │     │        ├─ logs/
│  │     │        └─ reports/
└─ config/
   ├─ tile_config.yaml
   ├─ run_config.yaml
   └─ VivadoProject/
```

### Notes
- `VivadoProject` is only notation in this specification.
- In the real filesystem, that folder has the real name of the active Vivado project.
- All persistent paths stored by the system are relative to `tiles/`.

---

## 3. Commands

AutoDoc V1 defines two logical commands:

### 3.1 Create tile base
Creates the base structure of a tile.

### 3.2 Create run
Creates a new documented run for an existing tile.

---

## 4. Tile Existence Rule

A tile is considered to exist if its root folder exists inside:

```text
database/tiles/<tile_id>/
```

The system does not use `records.csv` to determine whether a tile exists.

---

## 5. Tile ID

### 5.1 Format

```text
<id_prefix>-<YYMMDD><tile_number><id_version><id_revision>
```

### 5.2 Example

```text
MST130-01-26030600010102
```

### 5.3 Components

- `id_prefix`: manual, from `tile_config.yaml`
- `YYMMDD`: automatic, tile creation date
- `tile_number`: automatic, global 4-digit consecutive number from `tile_index.csv`
- `id_version`: manual, 2 digits, from `tile_config.yaml`
- `id_revision`: manual, 2 digits, from `tile_config.yaml`

### 5.4 Rules

- `tile_id` is generated once when the tile is created
- `tile_id` remains fixed for all future runs of that tile
- the tile root folder name is exactly `tile_id`

---

## 6. Run ID

There is no separate `run_id` object apart from the folder name.

### Format
```text
run-001
run-002
run-003
```

### Rules
- consecutive numbering is per tile
- the next run is determined by scanning valid run folders
- only folders matching `run-\d{3}` are considered
- invalid folders are ignored

---

## 7. CSV Files

## 7.1 tile_index.csv

### Purpose
Stores tile registrations only.

### Exact header

```csv
tile_number,tile_id,tile_name,tile_author
```

### Fields
- `tile_number`
- `tile_id`
- `tile_name`
- `tile_author`

### Sources
- `tile_number`: system
- `tile_id`: system
- `tile_name`: `tile_config.yaml`
- `tile_author`: `tile_config.yaml`

---

## 7.2 records.csv

### Purpose
Stores run registrations only.

### Exact header

```csv
Tile_ID,Run_ID,Date,Author,Objective,Status,Main_Change,Run_Path,Vivado_Version,Result_Summary,Tags
```

### Field sources
- `Tile_ID`: system
- `Run_ID`: system, folder name such as `run-001`
- `Date`: system, format `YYYY-MM-DD`
- `Author`: `run_config.yaml`
- `Objective`: `run_config.yaml`
- `Status`: `run_config.yaml`
- `Main_Change`: `run_config.yaml`
- `Run_Path`: system
- `Vivado_Version`: `run_config.yaml`
- `Result_Summary`: `run_config.yaml`
- `Tags`: `run_config.yaml`

### Run_Path format
```text
tiles/<tile_id>/runs/run-001
```

---

## 8. Configuration Files

## 8.1 tile_config.yaml

### Mandatory expected fields
- `id_prefix`
- `id_version`
- `id_revision`
- `tile_name`
- `tile_author`
- `ports`
- `usage_guide`
- `tb_description`

### Field types
- `id_prefix`: single-line text
- `id_version`: exactly 2 digits
- `id_revision`: exactly 2 digits
- `tile_name`: single-line text
- `tile_author`: single-line text
- `ports`: multiline free text
- `usage_guide`: multiline free text
- `tb_description`: multiline free text

### Template

```yaml
id_prefix: ""
id_version: ""
id_revision: ""

tile_name: ""
tile_author: ""

ports: |
  

usage_guide: |
  

tb_description: |
  
```

---

## 8.2 run_config.yaml

### Mandatory expected fields
- `run_author`
- `objective`
- `status`
- `vivado_version`
- `sim`
- `top`
- `seed`
- `sim_time`
- `summary`
- `key_warnings`
- `key_errors`
- `main_change`
- `tags`
- `notes`

### Single-line fields
- `run_author`
- `objective`
- `status`
- `vivado_version`
- `sim`
- `top`
- `seed`
- `sim_time`
- `tags`

### Multiline fields
- `summary`
- `key_warnings`
- `key_errors`
- `main_change`
- `notes`

### Allowed values for `status`
- `PASS`
- `FAIL`
- `WIP`
- `EXCLUDE`

### Template

```yaml
run_author: ""
objective: ""
status: ""

vivado_version: ""
sim: ""
top: ""
seed: ""
sim_time: ""
tags: ""

summary: |
  

key_warnings: |
  

key_errors: |
  

main_change: |
  

notes: |
  
```

---

## 9. Generated Files

## 9.1 README.md

### Purpose
General tile documentation.

### Sources
- `tile_id`: system
- `tile_name`: `tile_config.yaml`
- `ports`: `tile_config.yaml`
- `usage_guide`: `tile_config.yaml`
- `tb_description`: `tile_config.yaml`

### Generation rules
- generated when creating tile base
- regenerated on every run

### Template

```md
# Tile ID : "${tile_id}"

## Title: "${tile_name}"

## Port convention:
"${ports}"

## Usage guide:
"${usage_guide}"

## Testbench description:
"${tb_description}"
```

---

## 9.2 notes.md

### Purpose
Run note file.

### Sources
- `tile_id`: system
- `tile_name`: `tile_config.yaml`
- `notes`: `run_config.yaml`

### Template

```md
# Tile ID : "${tile_id}"

## Title: "${tile_name}"

## notes:
"${notes}"
```

---

## 9.3 manifest.yaml

### Purpose
Structured run manifest.

### Sources
- system values
- `run_config.yaml`
- copied file paths inside the run

### Template

```yaml
tile_id: ""
run_id: ""
date: ""
author: ""

objective: ""
status: ""

tools:
  vivado: ""
  simulator: ""

run_config:
  top: ""
  seed: ""
  sim_time: ""

sources:
  rtl: []
  tb: []
  constraints: []
  scripts: []

artifacts:
  sim_log: []
  wave: []

results:
  summary: ""
  key_warnings: ""
  key_errors: ""
```

### Field mapping
- `tile_id`: system
- `run_id`: system, format `run-001`
- `date`: system, format `YYYY-MM-DD`
- `author`: `run_config.yaml: run_author`
- `objective`: `run_config.yaml: objective`
- `status`: `run_config.yaml: status`

#### tools
- `vivado`: `run_config.yaml: vivado_version`
- `simulator`: `run_config.yaml: sim`

#### run_config
- `top`: `run_config.yaml: top`
- `seed`: `run_config.yaml: seed`
- `sim_time`: `run_config.yaml: sim_time`

#### sources
Always lists of relative paths from `tiles/`
- `rtl`
- `tb`
- `constraints`
- `scripts`

#### artifacts
Always lists of relative paths from `tiles/`
- `sim_log`
- `wave`

#### results
- `summary`: `run_config.yaml`
- `key_warnings`: `run_config.yaml`
- `key_errors`: `run_config.yaml`

---

## 10. Create Tile Base Flow

### Input
- `database/config/tile_config.yaml`

### Output
Creates:

```text
database/tiles/<tile_id>/
├─ README.md
├─ works/
└─ runs/
```

### Actions
1. read `tile_config.yaml`
2. obtain next global `tile_number` from `tile_index.csv`
3. generate `tile_id`
4. create `database/tiles/<tile_id>/`
5. create `README.md`
6. create `works/`
7. create `runs/`
8. add row to `tile_index.csv`

### Notes
- no run is created automatically
- if an internal `tile_id` collision occurs, the system marks an error

---

## 11. Create Run Flow

### Input
- target `tile_id`
- `database/config/run_config.yaml`
- `database/config/VivadoProject/`

### Actions
1. verify target tile exists
2. read `run_config.yaml`
3. determine next `run-001`-style folder name
4. create run folder
5. create run internal structure
6. copy snapshot of `run_config.yaml` to the run root
7. copy source files from Vivado project
8. copy generated artifacts from Vivado project
9. generate `manifest.yaml`
10. generate `notes.md`
11. regenerate tile `README.md`
12. update `works/`
13. append row to `records.csv`

---

## 12. Run Folder Structure

```text
run-001/
├─ run_config.yaml
├─ manifest.yaml
├─ notes.md
├─ src/
│  ├─ rtl/
│  ├─ tb/
│  ├─ constraints/
│  └─ scripts/
└─ out/
   ├─ sim/
   │  ├─ logs/
   │  └─ waves/
   ├─ synth/
   │  ├─ logs/
   │  └─ reports/
   └─ impl/
      ├─ logs/
      └─ reports/
```

---

## 13. works/ Rules

### Purpose
Represents the active source snapshot of the last documented run.

### Structure
- `works/rtl/`
- `works/tb/`
- `works/constraints/`
- `works/scripts/`

### Update rule
- clear all contents inside `works/`
- keep the `works/` folder itself
- copy the `src/` contents from the latest run
- destination is flat by category

---

## 14. Copy Rules

## 14.1 Source Origins

All source and artifact paths are relative to `VivadoProject`.

Current defined origins:

- `rtl` → `project_name/project_name.srcs/sources_1/new/`
- `tb` → `project_name/project_name.srcs/sim_1/new/`
- `constraints` → `project_name/project_name.srcs/constrs_1/`
- `scripts` → `project_name/`
- `sim/logs` → `project_name/project_name.sim/sim_1/behav/xsim/sources_1/new/`
- `sim/waves` → `project_name/project_name.sim/sim_1/behav/xsim/sources_1/new/`
- `synth/logs` → `project_name/project_name.runs/synth_1/`
- `synth/reports` → `project_name/project_name.runs/synth_1/`
- `impl/logs` → `project_name/project_name.runs/impl_1/`
- `impl/reports` → `project_name/project_name.runs/impl_1/`

### Origin interpretation
- all origins are searched recursively
- `constraints` collects `.xdc` files under the Vivado constraints tree
- `scripts` collects `.tcl` and `.py` files from the Vivado project tree

---

## 14.2 Accepted Extensions

- `rtl`: `.v`, `.sv`
- `tb`: `.v`, `.sv`
- `constraints`: `.xdc`
- `scripts`: `.tcl`, `.py`
- `logs`: `.log`
- `reports`: `.rpt`
- `waves`: `.wdb`

---

## 14.3 Copy Behavior

- recursive search in origin
- flat copy in destination
- no subfolder preservation
- copy all matching files for the category

### Name collisions
If duplicate names appear:
- `file.v`
- `file_1.v`
- `file_2.v`

### Missing categories
- do not stop the run
- represent them as `[]` in `manifest.yaml`

---

## 15. Path Persistence Rule

All paths stored by the system must be relative to the general `tiles/` folder.

### Examples
- `tiles/<tile_id>/runs/run-001/src/rtl/top.sv`
- `tiles/<tile_id>/runs/run-001/out/sim/logs/xsim.log`

This applies to:
- `manifest.yaml`
- `records.csv`
- any stored path generated by the system

---

## 16. Validation Rules

## 16.1 Mark error if missing
- `database/config/`
- `database/tiles/`
- `database/config/tile_config.yaml`
- `database/config/run_config.yaml`
- `database/config/VivadoProject/`
- `tile_index.csv`
- `records.csv`
- target tile when creating run

## 16.2 Mark error if invalid
- incorrect header in `tile_index.csv` when the file is non-empty
- incorrect header in `records.csv` when the file is non-empty
- `id_version` not exactly 2 digits
- `id_revision` not exactly 2 digits
- `status` outside `PASS | FAIL | WIP | EXCLUDE`

## 16.3 Continue normally if
- `tile_index.csv` exists but is empty
- `records.csv` exists but is empty
- expected fields inside YAML are missing
- one or more copy categories do not exist in Vivado project

## 16.4 CSV empty-file rule
If `tile_index.csv` or `records.csv` exists but is empty:
- the file is treated as valid but uninitialized
- header validation is skipped for that read
- the correct header is written before the first appended row

## 16.5 Empty field rendering
If a field is missing or empty, it is rendered as:

```text
""
```

---

## 17. Initial Numbering Rules

### tile_number
- if `tile_index.csv` exists and is empty, first `tile_number = 0001`
- otherwise, use max existing tile number + 1

### run number
- per tile
- if no valid runs exist, first run is `run-001`

---

## 18. Conceptual Model

AutoDoc follows a run-based documentation model:

- `config/` contains editable inputs for the active work context
- `tiles/` contains generated documentation and historical runs
- `tile_index.csv` stores tile identity records
- `records.csv` stores run history
- `works/` stores the latest active source snapshot
- each run is immutable once captured
