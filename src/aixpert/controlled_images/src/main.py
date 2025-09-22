"""Main function to unify all image generation scripts."""

#!/usr/bin/env python3
# main.py
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Callable, Dict, Iterator, List, Tuple

from image_utils import (
    gen_flux_png,
    gen_gemini_png,
    gen_grok_png,
    gen_openai_png,
    retryable,
    save_png,
)
from prompts import system_prompts
from utils import (
    append_rows,
    default_checkpoint_path,
    ensure_dirs,
    init_csv,
    load_config,
    log_row,
    materialize_prompts,
    merge_retries,
    resolve_api_key,
    save_checkpoint_atomic,
)


def bind_provider(
    provider_name: str,
    provider_cfg: dict,
    max_attempts: int,
    max_backoff: int,
) -> Callable[[str], bytes]:
    """
    Build and bind a generator for the selected provider.

    Return a bound `_gen(prompt) -> bytes` function
    for CSV logging.
    """
    # Get the API key once per provider
    api_key = resolve_api_key(provider_cfg)
    model_name = provider_cfg["model_name"]

    if provider_name == "flux":

        @retryable(max_attempts, max_backoff, "FAL generation")  # type: ignore[misc]
        def generate_png(prompt: str) -> bytes:
            return gen_flux_png(api_key, model_name, prompt)

        return generate_png

    if provider_name == "gemini":
        predict_url = provider_cfg["predict_url"]
        sample_count = provider_cfg["sample_count"]

        @retryable(max_attempts, max_backoff, "Gemini generation")  # type: ignore[misc]
        def generate_png(prompt: str) -> bytes:
            return gen_gemini_png(api_key, predict_url, prompt, sample_count)

        return generate_png

    if provider_name == "gpt":
        image_size = provider_cfg["image_size"]

        @retryable(max_attempts, max_backoff, "OpenAI generation")  # type: ignore[misc]
        def generate_png(prompt: str) -> bytes:
            return gen_openai_png(api_key, model_name, prompt, image_size)

        return generate_png

    if provider_name in ("grok", "sdxl"):
        # SDXL currently mirrors the Grok HTTP flow in the original code.
        image_format = provider_cfg["image_format"]

        @retryable(max_attempts, max_backoff, "Grok generation")  # type: ignore[misc]
        def generate_png(prompt: str) -> bytes:
            return gen_grok_png(api_key, model_name, prompt, image_format)

        return generate_png

    raise ValueError(f"Unknown provider: {provider_name}")


def handle_existing_file(
    out_path: Path,
    image_key: str,
    logged: set[str],
    csv_path: Path,
    prompt: str,
    category: str,
    model_for_csv: str,
    setting: str,
) -> bool:
    """
    Handle the case where the target PNG already exists.

    Ensure a CSV row exists for the image, and return True if the caller
    should skip generation (`continue`), otherwise False.
    """
    if out_path.exists():
        print(f"[SKIP:file] {image_key}")
        if image_key not in logged:
            log_row(csv_path, out_path, prompt, category, model_for_csv, setting)
            logged.add(image_key)
        return True
    return False


def iter_targets(
    prompts: Dict[str, Tuple[str, str]],
    num_samples: int,
    outdir: Path,
) -> Iterator[tuple[str, str, int, str, Path, str]]:
    """Yield (category, setting, s, prompt, out_path, image_key) for all targets."""
    for category, (baseline_prompt, controlled_prompt) in prompts.items():
        for setting, prompt in (
            ("baseline", baseline_prompt),
            ("controlled", controlled_prompt),
        ):
            for s in range(num_samples):
                filename = f"{category}_{setting}_s{s}.png"
                out_path = outdir / category / setting / filename
                image_key = str(out_path).replace("\\", "/")
                yield category, setting, s, prompt, out_path, image_key


def run(
    provider_name: str,
    prompts: Dict[str, Tuple[str, str]],
    common: dict,
    provider_cfg: dict,
) -> None:
    """Run a single configured provider."""
    num_samples = common["num_samples_per_setting"]
    retries = merge_retries(common, provider_cfg)
    max_attempts, max_backoff = retries["max_attempts"], retries["max_backoff"]

    outdir = Path(provider_cfg["outdir"])
    csv_path = Path(provider_cfg["csv_path"])
    ckpt_path = default_checkpoint_path(csv_path)

    # Prepare dirs/CSV
    ensure_dirs(outdir, prompts.keys())
    logged = init_csv(csv_path)

    # Provider binding
    _gen = bind_provider(provider_name, provider_cfg, max_attempts, max_backoff)
    model_name = provider_cfg["model_name"]

    # Buffer & flushing policy
    row_buffer: List[List[str]] = []
    flush_every: int = int(common.get("flush_every", 10))  # configurable; default 10

    total = generated = skipped_files = skipped_logged = failed = 0

    for category, setting, s, prompt, out_path, image_key in iter_targets(
        prompts, num_samples, outdir
    ):
        total += 1

        # If file exists, skip generation but ensure CSV row exists.
        if handle_existing_file(
            out_path,
            image_key,
            logged,
            csv_path,
            prompt,
            category,
            model_name,
            setting,
        ):
            skipped_files += 1
            continue

        # If already in CSV, still generate
        if image_key in logged:
            print(f"[SKIP:csv]  {image_key}")
            skipped_logged += 1

        print(f"[GEN:{provider_name}] {category} | {setting} | sample {s}")
        try:
            png_bytes = _gen(prompt)
            save_png(png_bytes, out_path)
            # Queue a row instead of logging immediately
            if image_key not in logged:
                row_buffer.append(
                    [
                        str(out_path).replace("\\", "/"),
                        prompt,
                        category,
                        model_name,
                        setting,
                    ]
                )
                # log_row(csv_path, out_path, prompt, category, model_name, setting)
                logged.add(image_key)
            generated += 1

            # Batch flush
            if len(row_buffer) >= flush_every:
                append_rows(csv_path, row_buffer)
                # checkpoint with a minimal payload
                save_checkpoint_atomic(
                    ckpt_path,
                    {
                        "provider": provider_name,
                        "last_category": category,
                        "last_setting": setting,
                        "last_index": s,
                        "generated_total": generated,
                        "csv_rows_flushed": len(row_buffer),
                    },
                )
                row_buffer.clear()

        except Exception as e:  # noqa: BLE001 (keep broad to match original robustness)
            print(f"[FAIL] {image_key}: {e}")
            failed += 1

    # Final flush
    if row_buffer:
        append_rows(csv_path, row_buffer)
        save_checkpoint_atomic(
            ckpt_path,
            {
                "provider": provider_name,
                "last_category": category,
                "last_setting": setting,
                "last_index": s,
                "generated_total": generated,
                "csv_rows_flushed": len(row_buffer),
                "final": True,
            },
        )
        row_buffer.clear()

    print("\nDone.")
    print(f"• Provider:                    {provider_name}")
    print(f"• Total targets:             {total}")
    print(f"• Generated new images:      {generated}")
    print(f"• Skipped (file existed):    {skipped_files}")
    print(f"• Skipped (already in CSV):  {skipped_logged}")
    print(f"• Failed:                    {failed}")
    print(f"• Images dir: {outdir}/<category>/<setting>/")
    print(f"• CSV:        {csv_path}")


def main() -> None:
    """
    CLI entry point for the unified image generation provider.

    Parse flags, load the config, determine which providers to execute,
    and invoke `run` for each.
    """
    parser = argparse.ArgumentParser(description="Unified image generation CLI")
    parser.add_argument(
        "--provider",
        choices=["gpt", "gemini", "flux", "grok", "sdxl", "all"],
        default="all",
        help="Which provider to execute (defaults to all enabled providers)",
    )
    parser.add_argument(
        "--config",
        default="configs/img_gen_config.yaml",
        help="Path to config.yaml",
    )
    args = parser.parse_args()
    prompts = materialize_prompts(system_prompts)
    cfg = load_config(args.config)
    common = cfg["common"]
    providers_cfg = cfg["providers"]

    # Determine which providers to run
    if args.provider == "all":
        provider_names = [
            name for name, rc in providers_cfg.items() if rc.get("enabled", False)
        ]
        if not provider_names:
            print(
                "No providers enabled in config.yaml. Use --provider to run one, or enable in the config."
            )
            return
    else:
        provider_names = [args.provider]

    for name in provider_names:
        rc = providers_cfg.get(name)
        if not rc:
            print(f"[WARN] Provider '{name}' missing in config.yaml → skipping.")
            continue
        run(name, prompts, common, rc)


if __name__ == "__main__":
    main()
