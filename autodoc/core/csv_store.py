"""
CSV persistence layer — Sections 7, 17 of AutoDoc V1 spec.

Handles tile_index.csv and records.csv.
- Writes header only when file is empty (section 16.4).
- All paths stored relative to tiles/ (section 15).
"""
import csv
from pathlib import Path

from core.validator import TILE_INDEX_HEADER, RECORDS_HEADER


# ──────────────────────────────────────────────
# tile_index.csv
# ──────────────────────────────────────────────

def read_tile_index(csv_path: Path) -> list[dict]:
    """Return all rows from tile_index.csv, or [] if empty."""
    content = csv_path.read_text(encoding="utf-8").strip()
    if not content:
        return []
    rows = list(csv.DictReader(content.splitlines()))
    return rows


def next_tile_number(csv_path: Path) -> int:
    """
    Section 17 — if empty → 1 (printed as 0001).
    Otherwise max(tile_number) + 1.
    """
    rows = read_tile_index(csv_path)
    if not rows:
        return 1
    numbers = [int(r["tile_number"]) for r in rows if r.get("tile_number", "").strip().isdigit()]
    return max(numbers) + 1 if numbers else 1


def append_tile_index_row(
    csv_path: Path,
    tile_number: int,
    tile_id: str,
    tile_name: str,
    tile_author: str,
) -> None:
    """
    Append one row to tile_index.csv.
    Writes header first if the file is empty (section 16.4).
    """
    is_empty = csv_path.read_text(encoding="utf-8").strip() == ""

    with csv_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if is_empty:
            writer.writerow(TILE_INDEX_HEADER)
        writer.writerow([f"{tile_number:04d}", tile_id, tile_name, tile_author])


# ──────────────────────────────────────────────
# records.csv
# ──────────────────────────────────────────────

def append_records_row(
    csv_path: Path,
    *,
    tile_id: str,
    run_id: str,
    date: str,
    author: str,
    objective: str,
    status: str,
    main_change: str,
    run_path: str,
    vivado_version: str,
    result_summary: str,
    tags: str,
) -> None:
    """
    Append one row to records.csv.
    Writes header first if the file is empty (section 16.4).
    run_path must already be relative to tiles/ (section 15).
    """
    is_empty = csv_path.read_text(encoding="utf-8").strip() == ""

    with csv_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if is_empty:
            writer.writerow(RECORDS_HEADER)
        writer.writerow([
            tile_id, run_id, date, author, objective, status,
            main_change, run_path, vivado_version, result_summary, tags,
        ])
