#!/usr/bin/env python3
"""
AutoDoc V1 — CLI entry point.

Usage:
  python cli.py create-tile --db ./database
  python cli.py create-run  --db ./database --tile <tile_id>
"""
import argparse
import sys
from pathlib import Path


def _resolve_db(db_arg: str) -> Path:
    p = Path(db_arg).resolve()
    if not p.exists():
        print(f"[ERROR] Database directory not found: {p}", file=sys.stderr)
        sys.exit(1)
    return p


def cmd_init_db(args: argparse.Namespace) -> None:
    from commands.init_db import run_init_db
    from core.validator import AutoDocError

    db_root = Path(args.db).resolve()
    try:
        run_init_db(db_root, force=args.force)
    except AutoDocError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_create_tile(args: argparse.Namespace) -> None:
    from commands.create_tile import run_create_tile
    from core.validator import AutoDocError

    db_root = _resolve_db(args.db)
    try:
        run_create_tile(db_root)
    except AutoDocError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_create_run(args: argparse.Namespace) -> None:
    from commands.create_run import run_create_run
    from core.validator import AutoDocError

    db_root = _resolve_db(args.db)
    tile_id = args.tile.strip()
    if not tile_id:
        print("[ERROR] --tile cannot be empty.", file=sys.stderr)
        sys.exit(1)

    try:
        run_create_run(db_root, tile_id)
    except AutoDocError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="autodoc",
        description="AutoDoc V1 — Vivado tile documentation workflow.",
    )
    parser.add_argument(
        "--db",
        default="./database",
        metavar="PATH",
        help="Path to the database/ root directory (default: ./database)",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # init ────────────────────────────────────────────────────────────────
    p_init = sub.add_parser(
        "init",
        help="Create the database/ skeleton with config templates.",
    )
    p_init.add_argument(
        "--force",
        action="store_true",
        help="Allow init inside an existing directory (skips existing files).",
    )
    p_init.set_defaults(func=cmd_init_db)

    # create-tile ─────────────────────────────────────────────────────────
    p_tile = sub.add_parser(
        "create-tile",
        help="Create a new tile base structure from tile_config.yaml.",
    )
    p_tile.set_defaults(func=cmd_create_tile)

    # create-run ──────────────────────────────────────────────────────────
    p_run = sub.add_parser(
        "create-run",
        help="Create a new documented run for an existing tile.",
    )
    p_run.add_argument(
        "--tile",
        required=True,
        metavar="TILE_ID",
        help="The tile_id of the target tile (e.g. MST130-01-26030600010102).",
    )
    p_run.set_defaults(func=cmd_create_run)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
