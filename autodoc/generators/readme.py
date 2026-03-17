"""
README.md generator — Section 9.1 of AutoDoc V1 spec.

Generated when creating tile base; regenerated on every run.
Template filled from tile_config.yaml fields and system-derived tile_id.
"""
from pathlib import Path

from models.tile_config import TileConfig

_TEMPLATE = '''\
# Tile ID : "{tile_id}"

## Title: "{tile_name}"

## Description:
"{description}"

## Port convention:
"{ports}"

## Usage guide:
"{usage_guide}"

## Testbench description:
"{tb_description}"
'''


def render_readme(tile_id: str, cfg: TileConfig) -> str:
    """Return the rendered README.md content."""
    return _TEMPLATE.format(
        tile_id=tile_id,
        tile_name=cfg.tile_name,
        description=cfg.description,
        ports=cfg.ports,
        usage_guide=cfg.usage_guide,
        tb_description=cfg.tb_description,
    )


def write_readme(tile_root: Path, tile_id: str, cfg: TileConfig) -> None:
    """Write README.md to the tile root directory."""
    content = render_readme(tile_id, cfg)
    (tile_root / "README.md").write_text(content, encoding="utf-8")
