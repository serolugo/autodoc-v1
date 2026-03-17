"""
notes.md generator — Section 9.2 of AutoDoc V1 spec.

Generated once per run.
Template filled from tile_config.yaml fields, system tile_id,
and run_config.yaml notes field.
"""
from pathlib import Path

from models.tile_config import TileConfig
from models.run_config import RunConfig

_TEMPLATE = '''\
# Tile ID : "{tile_id}"

## Title: "{tile_name}"

## notes:
"{notes}"
'''


def render_notes(tile_id: str, tile_cfg: TileConfig, run_cfg: RunConfig) -> str:
    """Return the rendered notes.md content."""
    return _TEMPLATE.format(
        tile_id=tile_id,
        tile_name=tile_cfg.tile_name,
        notes=run_cfg.notes,
    )


def write_notes(run_root: Path, tile_id: str, tile_cfg: TileConfig, run_cfg: RunConfig) -> None:
    """Write notes.md to the run root directory."""
    content = render_notes(tile_id, tile_cfg, run_cfg)
    (run_root / "notes.md").write_text(content, encoding="utf-8")
