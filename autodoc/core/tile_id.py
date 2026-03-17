"""
Tile ID generation — Section 5 of AutoDoc V1 spec.

Format: <id_prefix>-<YYMMDD><tile_number:04d><id_version><id_revision>
Example: MST130-01-26030600010102
"""
from datetime import date


def generate_tile_id(
    id_prefix: str,
    id_version: str,
    id_revision: str,
    tile_number: int,
    creation_date: date | None = None,
) -> str:
    """
    Build the tile_id string from its components.

    - id_prefix     : from tile_config.yaml (e.g. "MST130-01")
    - id_version    : 2-digit string from tile_config.yaml
    - id_revision   : 2-digit string from tile_config.yaml
    - tile_number   : 4-digit global consecutive number
    - creation_date : date of tile creation (defaults to today)
    """
    if creation_date is None:
        creation_date = date.today()

    yymmdd = creation_date.strftime("%y%m%d")
    tile_num_str = f"{tile_number:04d}"

    return f"{id_prefix}-{yymmdd}{tile_num_str}{id_version}{id_revision}"
