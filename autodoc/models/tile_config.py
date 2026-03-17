from dataclasses import dataclass


@dataclass
class TileConfig:
    id_prefix: str
    id_version: str
    id_revision: str
    tile_name: str
    tile_author: str
    description: str
    ports: str
    usage_guide: str
    tb_description: str

    REQUIRED_FIELDS = [
        "id_prefix", "id_version", "id_revision",
        "tile_name", "tile_author",
        "description", "ports", "usage_guide", "tb_description",
    ]

    @classmethod
    def from_dict(cls, data: dict) -> "TileConfig":
        def _get(key: str) -> str:
            val = data.get(key, "")
            return str(val).strip() if val is not None else ""

        return cls(
            id_prefix=_get("id_prefix"),
            id_version=_get("id_version"),
            id_revision=_get("id_revision"),
            tile_name=_get("tile_name"),
            tile_author=_get("tile_author"),
            description=_get("description"),
            ports=_get("ports"),
            usage_guide=_get("usage_guide"),
            tb_description=_get("tb_description"),
        )
