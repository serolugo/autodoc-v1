"""
Standalone test runner — no pytest required.
Run from autodoc/:  python tests/runner.py
"""
import sys
import traceback
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.test_autodoc import (
    # helpers are imported inline inside each test
    test_tile_id_format,
    test_tile_id_tile_number_padding,
    test_run_id_empty_dir,
    test_run_id_after_existing,
    test_run_id_ignores_invalid_folders,
    test_create_tile_basic,
    test_create_tile_tile_index_row,
    test_create_tile_readme_content,
    test_create_tile_invalid_id_version,
    test_create_tile_invalid_id_revision,
    test_create_tile_consecutive_numbering,
    test_create_run_structure,
    test_create_run_files_copied,
    test_create_run_manifest_paths_relative,
    test_create_run_records_csv_row,
    test_create_run_works_updated,
    test_create_run_invalid_status,
    test_create_run_tile_not_found,
    test_create_run_consecutive,
    test_init_db_creates_structure,
    test_init_db_yaml_templates_not_empty,
    test_init_db_csv_files_empty,
    test_init_db_existing_dir_raises,
    test_init_db_force_skips_existing,
    test_init_db_then_create_tile,
    test_bad_tile_index_header,
    test_bad_records_header,
    test_empty_csv_header_skipped,
    test_copy_flat_collision,
    test_copy_missing_origin_returns_empty,
)

# Tests that need a tmp_path argument
NEEDS_TMP = {
    test_run_id_empty_dir,
    test_run_id_after_existing,
    test_run_id_ignores_invalid_folders,
    test_create_tile_basic,
    test_create_tile_tile_index_row,
    test_create_tile_readme_content,
    test_create_tile_invalid_id_version,
    test_create_tile_invalid_id_revision,
    test_create_tile_consecutive_numbering,
    test_create_run_structure,
    test_create_run_files_copied,
    test_create_run_manifest_paths_relative,
    test_create_run_records_csv_row,
    test_create_run_works_updated,
    test_create_run_invalid_status,
    test_create_run_tile_not_found,
    test_create_run_consecutive,
    test_init_db_creates_structure,
    test_init_db_yaml_templates_not_empty,
    test_init_db_csv_files_empty,
    test_init_db_existing_dir_raises,
    test_init_db_force_skips_existing,
    test_init_db_then_create_tile,
    test_bad_tile_index_header,
    test_bad_records_header,
    test_empty_csv_header_skipped,
    test_copy_flat_collision,
    test_copy_missing_origin_returns_empty,
}

ALL_TESTS = [
    test_tile_id_format,
    test_tile_id_tile_number_padding,
    test_run_id_empty_dir,
    test_run_id_after_existing,
    test_run_id_ignores_invalid_folders,
    test_create_tile_basic,
    test_create_tile_tile_index_row,
    test_create_tile_readme_content,
    test_create_tile_invalid_id_version,
    test_create_tile_invalid_id_revision,
    test_create_tile_consecutive_numbering,
    test_create_run_structure,
    test_create_run_files_copied,
    test_create_run_manifest_paths_relative,
    test_create_run_records_csv_row,
    test_create_run_works_updated,
    test_create_run_invalid_status,
    test_create_run_tile_not_found,
    test_create_run_consecutive,
    test_init_db_creates_structure,
    test_init_db_yaml_templates_not_empty,
    test_init_db_csv_files_empty,
    test_init_db_existing_dir_raises,
    test_init_db_force_skips_existing,
    test_init_db_then_create_tile,
    test_bad_tile_index_header,
    test_bad_records_header,
    test_empty_csv_header_skipped,
    test_copy_flat_collision,
    test_copy_missing_origin_returns_empty,
]


def run_all():
    passed = []
    failed = []

    for test_fn in ALL_TESTS:
        name = test_fn.__name__
        tmp = None
        try:
            if test_fn in NEEDS_TMP:
                tmp = Path(tempfile.mkdtemp())
                test_fn(tmp)
            else:
                test_fn()
            passed.append(name)
            print(f"  ✓  {name}")
        except Exception:
            failed.append(name)
            print(f"  ✗  {name}")
            traceback.print_exc()
        finally:
            if tmp and tmp.exists():
                shutil.rmtree(tmp)

    print()
    print("=" * 60)
    print(f"Results: {len(passed)} passed, {len(failed)} failed")
    if failed:
        print("FAILED:")
        for n in failed:
            print(f"  - {n}")
        sys.exit(1)
    else:
        print("ALL TESTS PASSED ✓")


if __name__ == "__main__":
    run_all()
