from dataclasses import dataclass

VALID_STATUSES = {"PASS", "FAIL", "WIP", "EXCLUDE"}


@dataclass
class RunConfig:
    run_author: str
    objective: str
    status: str
    vivado_version: str
    sim: str
    top: str
    seed: str
    sim_time: str
    constraints_used: bool
    tags: str
    summary: str
    key_warnings: str
    key_errors: str
    main_change: str
    notes: str

    REQUIRED_FIELDS = [
        "run_author", "objective", "status",
        "vivado_version", "sim", "top", "seed", "sim_time", "constraints_used", "tags",
        "summary", "key_warnings", "key_errors", "main_change", "notes",
    ]

    @classmethod
    def from_dict(cls, data: dict) -> "RunConfig":
        def _get(key: str) -> str:
            val = data.get(key, "")
            return str(val).strip() if val is not None else ""

        def _get_bool(key: str) -> bool:
            val = data.get(key, False)
            if isinstance(val, bool):
                return val
            return str(val).strip().lower() in ("true", "1", "yes")

        return cls(
            run_author=_get("run_author"),
            objective=_get("objective"),
            status=_get("status"),
            vivado_version=_get("vivado_version"),
            sim=_get("sim"),
            top=_get("top"),
            seed=_get("seed"),
            sim_time=_get("sim_time"),
            constraints_used=_get_bool("constraints_used"),
            tags=_get("tags"),
            summary=_get("summary"),
            key_warnings=_get("key_warnings"),
            key_errors=_get("key_errors"),
            main_change=_get("main_change"),
            notes=_get("notes"),
        )
