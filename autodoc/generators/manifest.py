"""
manifest.yaml generator — Section 9.3 of AutoDoc V1 spec.

Generated as a structured data dict, serialized with a custom writer
that adds blank lines between logical sections for readability.
All paths are relative to tiles/ (section 15).
"""
from pathlib import Path

from models.run_config import RunConfig


def _relative_to_tiles(path: Path, tiles_root: Path) -> str:
    """Convert an absolute path to a tiles/-relative string."""
    try:
        rel = path.relative_to(tiles_root)
        return "tiles/" + rel.as_posix()
    except ValueError:
        return path.as_posix()


def _paths_to_relative(paths: list[Path], tiles_root: Path) -> list[str]:
    return [_relative_to_tiles(p, tiles_root) for p in paths]


def _fmt_str(value: str) -> str:
    """Format a scalar string value for YAML."""
    if not value:
        return '""'
    # Quote if contains special chars
    if any(c in value for c in (':', '#', '{', '}', '[', ']', ',', '&', '*', '?', '|', '-', '<', '>', '=', '!', '%', '@', '`')):
        escaped = value.replace('"', '\\"')
        return f'"{escaped}"'
    return f'"{value}"'


def _fmt_bool(value: bool) -> str:
    return "true" if value else "false"


def _fmt_list(items: list[str], indent: int = 2) -> str:
    """Format a list as YAML block sequence."""
    if not items:
        return "[]"
    pad = " " * indent
    lines = "\n" + "".join(f"{pad}- {_fmt_str(i)}\n" for i in items)
    return lines.rstrip()


def build_manifest(
    *,
    tile_id: str,
    run_id: str,
    date: str,
    run_cfg: RunConfig,
    copied_sources: dict[str, list[Path]],
    copied_artifacts: dict[str, list[Path]],
    tiles_root: Path,
) -> dict:
    """Build the manifest data dict (used by tests and write_manifest)."""
    def rel(paths: list[Path]) -> list[str]:
        return _paths_to_relative(paths, tiles_root)

    return {
        "tile_id":  tile_id,
        "run_id":   run_id,
        "date":     date,
        "author":   run_cfg.run_author,
        "objective": run_cfg.objective,
        "status":   run_cfg.status,
        "tools": {
            "vivado":    run_cfg.vivado_version,
            "simulator": run_cfg.sim,
        },
        "run_config": {
            "top":              run_cfg.top,
            "seed":             run_cfg.seed,
            "sim_time":         run_cfg.sim_time,
            "constraints_used": run_cfg.constraints_used,
        },
        "sources": {
            "rtl":         rel(copied_sources.get("rtl", [])),
            "tb":          rel(copied_sources.get("tb", [])),
            "constraints": rel(copied_sources.get("constraints", [])),
            "scripts":     rel(copied_sources.get("scripts", [])),
        },
        "artifacts": {
            "sim_log": rel(copied_artifacts.get("sim_logs", [])),
            "wave":    rel(copied_artifacts.get("waves", [])),
        },
        "results": {
            "summary":      run_cfg.summary,
            "key_warnings": run_cfg.key_warnings,
            "key_errors":   run_cfg.key_errors,
        },
    }


def _render_manifest(m: dict) -> str:
    """
    Serialize manifest dict to a YAML string with visual blank-line spacing.
    Blank lines are inserted after: author, status, simulator, sim_time, scripts, wave.
    """
    tools      = m["tools"]
    rc         = m["run_config"]
    sources    = m["sources"]
    artifacts  = m["artifacts"]
    results    = m["results"]

    lines = [
        f'tile_id: {_fmt_str(m["tile_id"])}',
        f'run_id:  {_fmt_str(m["run_id"])}',
        f'date:    {_fmt_str(m["date"])}',
        f'author:  {_fmt_str(m["author"])}',
        "",                                              # ← blank after author
        f'objective: {_fmt_str(m["objective"])}',
        f'status:    {_fmt_str(m["status"])}',
        "",                                              # ← blank after status
        "tools:",
        f'  vivado:    {_fmt_str(tools["vivado"])}',
        f'  simulator: {_fmt_str(tools["simulator"])}',
        "",                                              # ← blank after simulator
        "run_config:",
        f'  top:              {_fmt_str(rc["top"])}',
        f'  seed:             {_fmt_str(rc["seed"])}',
        f'  sim_time:         {_fmt_str(rc["sim_time"])}',
        f'  constraints_used: {_fmt_bool(rc["constraints_used"])}',
        "",                                              # ← blank after sim_time block
        "sources:",
        f'  rtl:         {_fmt_list(sources["rtl"], indent=4)}',
        f'  tb:          {_fmt_list(sources["tb"], indent=4)}',
        f'  constraints: {_fmt_list(sources["constraints"], indent=4)}',
        f'  scripts:     {_fmt_list(sources["scripts"], indent=4)}',
        "",                                              # ← blank after scripts
        "artifacts:",
        f'  sim_log: {_fmt_list(artifacts["sim_log"], indent=4)}',
        f'  wave:    {_fmt_list(artifacts["wave"], indent=4)}',
        "",                                              # ← blank after wave
        "results:",
        f'  summary:      {_fmt_str(results["summary"])}',
        f'  key_warnings: {_fmt_str(results["key_warnings"])}',
        f'  key_errors:   {_fmt_str(results["key_errors"])}',
        "",
    ]
    return "\n".join(lines)


def write_manifest(run_root: Path, manifest: dict) -> None:
    """Write manifest.yaml to the run root directory."""
    content = _render_manifest(manifest)
    (run_root / "manifest.yaml").write_text(content, encoding="utf-8")

