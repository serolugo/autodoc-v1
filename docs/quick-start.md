# AutoDoc V1 — Quick Reference

## Installation

```powershell
# 1. Make sure you have Python 3.10 or higher
python --version

# 2. Install the only required dependency
pip install PyYAML

# 3. Verify everything works
cd "C:\path\to\Autodoc"
python tests\runner.py
# Expected: Results: 30 passed, 0 failed — ALL TESTS PASSED
```

---

## First time setup

```powershell
# 1. Initialize a new database
python cli.py --db "C:\path\to\database" init

# 2. Fill in the tile config
#    Edit: database\config\tile_config.yaml

# 3. Create your first tile
python cli.py --db "C:\path\to\database" create-tile
#    → saves the Tile ID printed in the output

# 4. Paste your Vivado project inside:
#    database\config\

# 5. Fill in the run config
#    Edit: database\config\run_config.yaml

# 6. Create your first run
python cli.py --db "C:\path\to\database" create-run --tile <tile_id>
```

---

## Every new run

```powershell
# 1. Update your Vivado project inside database\config\
# 2. Edit database\config\run_config.yaml
# 3. Run:
python cli.py --db "C:\path\to\database" create-run --tile <tile_id>
```

---

## Every new tile

```powershell
# 1. Edit database\config\tile_config.yaml
# 2. Run:
python cli.py --db "C:\path\to\database" create-tile
#    → save the new Tile ID
```

---

## All commands

| Command | Description |
|---|---|
| `init` | Create a new database skeleton |
| `init --force` | Init inside an existing folder without overwriting |
| `create-tile` | Create a new tile from tile_config.yaml |
| `create-run --tile <id>` | Document a run for an existing tile |

---

## Status values

| Value | Meaning |
|---|---|
| `PASS` | Run completed successfully |
| `FAIL` | Run produced errors |
| `WIP` | Work in progress |
| `EXCLUDE` | Excluded from analysis |

---

## Run the tests

```powershell
cd "C:\path\to\Autodoc"
python tests\runner.py
# Expected: Results: 30 passed, 0 failed
```

---

## Your current setup

```
C:\Residencia_lugo\Auto_doc_pruebas\
├── Autodoc\        ← code
└── database\       ← data
    ├── tile_index.csv
    ├── records.csv
    ├── tiles\
    │   └── MST130-01-26031500010101\
    └── config\
        ├── tile_config.yaml
        ├── run_config.yaml
        └── <VivadoProject>\
```

```powershell
# Your exact commands:
cd "C:\Residencia_lugo\Auto_doc_pruebas\Autodoc"

python cli.py --db "C:\Residencia_lugo\Auto_doc_pruebas\database" create-tile
python cli.py --db "C:\Residencia_lugo\Auto_doc_pruebas\database" create-run --tile MST130-01-26031500010101
```
