"""
Copy rules — Section 14 of AutoDoc V1 spec.

Origins are relative to VivadoProject root (the single subdir inside config/).
- Recursive search in origin directory.
- Flat copy in destination (no subfolder preservation).
- Name collisions resolved with _1, _2 suffixes.
- Missing categories do not stop the run → return [].
"""
import shutil
from pathlib import Path

# ──────────────────────────────────────────────
# Section 14.2 — accepted extensions per category
# ──────────────────────────────────────────────
CATEGORY_EXTENSIONS: dict[str, set[str]] = {
    "rtl":          {".v", ".sv"},
    "tb":           {".v", ".sv"},
    "constraints":  {".xdc"},
    "scripts":      {".tcl", ".py"},
    "sim_logs":     {".log"},
    "synth_logs":   {".log"},
    "impl_logs":    {".log"},
    "sim_reports":  {".rpt"},   # not used by spec, but kept for symmetry
    "synth_reports":{".rpt"},
    "impl_reports": {".rpt"},
    "waves":        {".wdb"},
}


def _resolve_vivado_project_root(vivado_dir: Path) -> tuple[Path, str]:
    """
    Resolve the actual Vivado project directory and project name.

    Handles two layouts:

    Layout A — project folder is directly vivado_dir itself:
      config/
        tile_16bit_adder/          ← vivado_dir
          tile_16bit_adder.srcs/
          tile_16bit_adder.sim/
          tile_16bit_adder.runs/

    Layout B — project folder is a subdirectory inside vivado_dir:
      config/
        VivadoWrapper/             ← vivado_dir
          my_proj/                 ← project_dir
            my_proj.srcs/
            my_proj.sim/
            my_proj.runs/

    Detection: if vivado_dir itself contains .srcs / .sim / .runs folders
    whose name starts with vivado_dir.name → Layout A.
    Otherwise fall back to Layout B (first subdir).
    """
    dir_name = vivado_dir.name

    # Check Layout A: .srcs folder named <dir_name>.srcs exists directly inside
    srcs_candidate = vivado_dir / f"{dir_name}.srcs"
    if srcs_candidate.exists():
        return vivado_dir, dir_name

    # Layout B: look for a single project subdirectory
    subdirs = [p for p in vivado_dir.iterdir() if p.is_dir()]
    if not subdirs:
        raise ValueError(f"No project subfolder found inside {vivado_dir}")
    subdirs = sorted(subdirs)
    project_dir = subdirs[0]
    return project_dir, project_dir.name


# ──────────────────────────────────────────────
# Section 14.1 — origin paths per category
# ──────────────────────────────────────────────
def _origin_paths(project_dir: Path, project_name: str) -> dict[str, Path]:
    pn = project_name
    srcs = project_dir / f"{pn}.srcs"
    sim_xsim = project_dir / f"{pn}.sim" / "sim_1" / "behav" / "xsim"
    runs = project_dir / f"{pn}.runs"

    return {
        "rtl":           srcs / "sources_1" / "new",
        "tb":            srcs / "sim_1"     / "new",
        "constraints":   srcs / "constrs_1",
        "scripts":       project_dir,
        "sim_logs":      sim_xsim,
        "waves":         sim_xsim,
        "synth_logs":    runs / "synth_1",
        "synth_reports": runs / "synth_1",
        "impl_logs":     runs / "impl_1",
        "impl_reports":  runs / "impl_1",
    }


# ──────────────────────────────────────────────
# Flat copy helpers
# ──────────────────────────────────────────────
def _unique_name(dest_dir: Path, name: str) -> Path:
    """
    Section 14.3 — collision resolution: file.v → file_1.v → file_2.v
    """
    stem = Path(name).stem
    suffix = Path(name).suffix
    candidate = dest_dir / name
    if not candidate.exists():
        return candidate
    counter = 1
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        candidate = dest_dir / new_name
        if not candidate.exists():
            return candidate
        counter += 1


def _copy_flat(origin: Path, dest: Path, extensions: set[str]) -> list[Path]:
    """
    Recursively find files with matching extensions in origin,
    copy them flat into dest. Returns list of copied destination paths.
    Missing origin → returns [] (section 16.3 / 14.3).
    """
    if not origin.exists():
        return []

    copied: list[Path] = []
    dest.mkdir(parents=True, exist_ok=True)

    for src_file in sorted(origin.rglob("*")):
        if src_file.is_file() and src_file.suffix in extensions:
            dst_file = _unique_name(dest, src_file.name)
            shutil.copy2(src_file, dst_file)
            copied.append(dst_file)

    return copied


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────
def copy_sources(vivado_dir: Path, run_src: Path) -> dict[str, list[Path]]:
    """
    Copy source files (rtl, tb, constraints, scripts) from VivadoProject
    into run_src/<category>/.

    Returns dict mapping category → list of copied destination paths.
    """
    project_dir, project_name = _resolve_vivado_project_root(vivado_dir)
    origins = _origin_paths(project_dir, project_name)

    results: dict[str, list[Path]] = {}
    for cat in ("rtl", "tb", "constraints", "scripts"):
        results[cat] = _copy_flat(
            origins[cat],
            run_src / cat,
            CATEGORY_EXTENSIONS[cat],
        )
    return results


def copy_artifacts(vivado_dir: Path, run_out: Path) -> dict[str, list[Path]]:
    """
    Copy generated artifacts (logs, reports, waves) from VivadoProject
    into run_out/<category>/.

    Returns dict mapping logical key → list of copied destination paths.
    """
    project_dir, project_name = _resolve_vivado_project_root(vivado_dir)
    origins = _origin_paths(project_dir, project_name)

    dest_map = {
        "sim_logs":      run_out / "sim"   / "logs",
        "waves":         run_out / "sim"   / "waves",
        "synth_logs":    run_out / "synth" / "logs",
        "synth_reports": run_out / "synth" / "reports",
        "impl_logs":     run_out / "impl"  / "logs",
        "impl_reports":  run_out / "impl"  / "reports",
    }

    results: dict[str, list[Path]] = {}
    for key, dest in dest_map.items():
        results[key] = _copy_flat(
            origins[key],
            dest,
            CATEGORY_EXTENSIONS[key],
        )
    return results
