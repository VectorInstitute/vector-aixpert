"""
Shared utilities for configuration, environment, filesystem, and CSV.

This module includes helpers to load YAML config, read API keys from `.env`,
ensure the expected output directory structure, and initialize/append to the
annotations CSV in a resume-safe way.
"""

# utils.py
from __future__ import annotations

import csv
import json
import os
import tempfile
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import yaml
from decouple import AutoConfig


# ---------- Config loading ----------


def load_config(path: Path | str = "config.yaml") -> dict:
    """
    Load the YAML configuration file into a Python dict.

    Args:
      path: Path to the YAML file (absolute or relative).

    Returns
    -------
      A dictionary parsed from the YAML file.

    Raises
    ------
      FileNotFoundError: If the file does not exist.
      yaml.YAMLError: If the YAML is malformed.
    """
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def materialize_prompts(
    prompts_cfg: Dict[str, Dict[str, str]],
) -> Dict[str, Tuple[str, str]]:
    """Convert {key: {short, long}} -> {key: (short, long)}."""
    return {k: (v["short"], v["long"]) for k, v in prompts_cfg.items()}


def merge_retries(common: dict, provider: dict) -> dict:
    """
    Merge global and provider-specific retry configs.

    provider overrides (if present) take precedence over common settings.

    Args:
      common: Dict that may contain:
      {"retries": {"max_attempts": int, "max_backoff": int}}.
      provider: Dict that may optionally contain its own {"retries": ...}.

    Returns
    -------
      A dict {"max_attempts": int, "max_backoff": int} usable by callers.
    """
    base = common.get("retries", {}) or {}
    override = provider.get("retries", {}) or {}
    return {**base, **override}


# ---------- Environment keys ----------

# Decouple config: looks for .env starting from CWD upward.
# For fixed project root, pass search_path=<path>.
DEC = AutoConfig()  # default: searches from os.getcwd()


def get_secret(var_name: str, default: str | None = None) -> str:
    """
    Read a secret from decouple (OS env first, then .env).

    Does not mutate os.environ.
    """
    val = DEC(var_name, default=default)
    if not val:
        raise RuntimeError(
            f"{var_name} not found. Provide providers.<name>.api_key in config.yaml, "
            f"or define {var_name} in a .env / environment."
        )
    return val


def resolve_api_key(provider_cfg: dict) -> str:
    """
    Return the API key for a provider.

    Precedence:
    1) Use `provider_cfg['api_key']` if present (literal in YAML).
    2) Otherwise read the environment variable named by `provider_cfg['env_var']`
       (via `decouple`).
    Raise a `RuntimeError` if neither is provided.
    """
    direct = provider_cfg.get("api_key")
    if direct:
        return direct
    env_var = provider_cfg.get("env_key")
    if env_var:
        return get_secret(env_var)
    raise RuntimeError(
        "No API key configured. Add an 'api_key' config under providers.<name> in config.yaml or an environment variable in `.env` file. "
    )


# ---------- Filesystem helpers ----------


def ensure_dirs(outdir: Path, categories: Iterable[str]) -> None:
    """Create expected output directories for each category and setting.

    The structure created is:
      <outdir>/<category>/baseline/
      <outdir>/<category>/controlled/

    Args:
      outdir: Root output directory.
      categories: Iterable of category names (e.g., "ceo", "nurse", ...).

    Returns
    -------
      None. Directories are created as a side effect.
    """
    outdir.mkdir(parents=True, exist_ok=True)
    for cat in categories:
        (outdir / cat / "baseline").mkdir(parents=True, exist_ok=True)
        (outdir / cat / "controlled").mkdir(parents=True, exist_ok=True)


# ---------- CSV helpers (resume-safe) ----------

CSV_HEADER = [
    "image_file",
    "prompt",
    "category",
    "model",
    "setting",
]


def init_csv(csv_path: Path) -> set[str]:
    """Ensure CSV exists; return set of already-logged image_file paths."""
    logged: set[str] = set()
    if csv_path.exists():
        with open(csv_path, "r", encoding="utf-8", newline="") as f:
            rd = csv.reader(f)
            _ = next(rd, None)  # header
            for row in rd:
                if row:
                    logged.add(row[0])
    else:
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            wr = csv.writer(f)
            wr.writerow(CSV_HEADER)
    return logged


def log_row(
    csv_path: Path,
    image_path: Path,
    prompt: str,
    category: str,
    model: str,
    setting: str,
) -> None:
    """Append a single generation record to the annotations CSV.

    Writes a row with the normalized image path

    Args:
      csv_path: Path to the annotations CSV.
      image_path: Path to the generated image file.
      prompt: The prompt used for generation.
      category: Prompt category (e.g., "ceo", "nurse").
      model: Model identifier recorded in the CSV (e.g., "dall-e-3").
      setting: Either "baseline" or "controlled".

    Returns
    -------
      None. Row is appended as a side effect.

    Raises
    ------
      OSError: If the CSV cannot be opened for append.
      csv.Error: If CSV writing fails.
    """
    with open(csv_path, "a", encoding="utf-8", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(
            [
                str(image_path).replace("\\", "/"),
                prompt,
                category,
                model,
                setting,
            ]
        )


# ---------- Batched CSV append ----------


def append_rows(csv_path: Path, rows: Iterable[List[str]]) -> None:
    """Append many rows to the CSV using a single open."""
    if not rows:
        return
    with open(csv_path, "a", encoding="utf-8", newline="") as f:
        wr = csv.writer(f)
        wr.writerows(rows)


# ---------- Checkpoint helpers ----------


def default_checkpoint_path(csv_path: Path) -> Path:
    """
    Derive a checkpoint file path from the CSV path.

    Example: annotations.csv -> annotations.csv.ckpt.json
    """
    return csv_path.with_name(csv_path.name + ".ckpt.json")


def load_checkpoint(ckpt_path: Path) -> dict | None:
    """Load checkpoint JSON if present; otherwise return None."""
    if not ckpt_path.exists():
        return None
    try:
        with open(ckpt_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def save_checkpoint_atomic(ckpt_path: Path, data: dict) -> None:
    """
    Atomically write checkpoint JSON to disk.

    Uses a temp file + rename to avoid partial writes.
    """
    ckpt_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=ckpt_path.name, dir=str(ckpt_path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, ckpt_path)
    finally:
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except Exception:
            pass
