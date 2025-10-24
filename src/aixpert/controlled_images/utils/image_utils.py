"""Utility functions for image generation and saving."""

# image_utils.py
from __future__ import annotations

import base64
import functools
import time
from pathlib import Path
from typing import Any, Callable, Literal, Optional, ParamSpec, TypeVar, cast

# from typing_extensions import ParamSpec, TypeVar
import openai
import requests


OpenAIImageSize = Literal[
    "auto",
    "256x256",
    "512x512",
    "1024x1024",
    "1536x1024",
    "1024x1536",
    "1792x1024",
    "1024x1792",
]


# ---------- Shared file helper ----------


def save_png(png_bytes: bytes, out_path: Path) -> None:
    """Save PNG bytes to out_path, creating parent dirs as needed."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(png_bytes)


# ---------- Retry Decorator ----------

# Type variable for decorator
P = ParamSpec("P")
T = TypeVar("T")


def retryable(
    max_attempts: int,
    max_backoff: int,
    label: str,
    should_retry: Optional[Callable[[Exception], bool]] = None,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorate a function with exponential backoff retries.

    The wrapped function is called up to `max_attempts` times. On failure,
    delays grow 2, 4, 8, ... seconds, capped by `max_backoff`. If `should_retry`
    is provided and returns False for an exception, the exception is raised
    immediately (no further retries).

    Args:
      max_attempts: Maximum number of attempts before giving up.
      max_backoff: Maximum backoff delay in seconds.
      label: Human-readable label printed in warnings (e.g., "OpenAI generation").
      should_retry: Optional predicate to decide whether an exception is retryable.
      sleep_fn: Sleep function to use (defaults to time.sleep); injectable for tests.

    Returns
    -------
      A decorator that adds retry logic to the target function.
    """

    def _decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def _wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            last_err: Optional[Exception] = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:  # noqa: BLE001
                    last_err = e
                    if should_retry is not None and not should_retry(e):
                        raise
                    if attempt >= max_attempts:
                        break
                    backoff = min(2 * (2 ** (attempt - 1)), max_backoff)
                    print(
                        f"[WARN] {label} attempt {attempt}/{max_attempts} failed: {e}. "
                        f"Retrying in {backoff}s..."
                    )
                    sleep_fn(backoff)
            raise RuntimeError(
                f"{label} failed after {max_attempts} attempts: {last_err}"
            ) from last_err

        return _wrapper

    return _decorator


# ---------- Providers ----------


def gen_flux_png(api_key: str, model_name: str, prompt: str) -> bytes:
    """Generate a PNG via FAL.ai and return its bytes (single attempt).

    Flow:
      1) POST https://fal.run/{model_name} with JSON payload {prompt, num_images: 1}
      2) Extract images[0].url from JSON
      3) GET the image URL and return the bytes
    """
    url = f"https://fal.run/{model_name}"
    headers = {"Authorization": f"Key {api_key}", "Content-Type": "application/json"}
    payload = {"prompt": prompt, "num_images": 1, "enable_safety_checker": False}

    r = requests.post(url, headers=headers, json=payload, timeout=120)
    r.raise_for_status()
    data = r.json()
    if "images" in data and data["images"]:
        img_url = data["images"][0]["url"]
        rr = requests.get(img_url, timeout=120)
        rr.raise_for_status()
        return rr.content
    raise RuntimeError("No image data in response")


def gen_gemini_png(
    api_key: str, predict_url: str, prompt: str, sample_count: int
) -> bytes:
    """Generate a PNG via Google Imagen-4 (single attempt)."""
    headers = {"x-goog-api-key": api_key, "Content-Type": "application/json"}
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {"sampleCount": sample_count},
    }

    r = requests.post(predict_url, headers=headers, json=payload, timeout=120)
    r.raise_for_status()
    data = r.json()

    preds = data.get("predictions") or data.get("candidates") or []
    b64 = None
    if preds:
        p0 = preds[0]
        if isinstance(p0, dict) and "bytesBase64Encoded" in p0:
            b64 = p0["bytesBase64Encoded"]
        elif isinstance(p0, dict) and "image" in p0:
            img = p0["image"]
            b64 = img.get("bytesBase64Encoded") or img.get("imageBytes")

    if not b64:
        raise RuntimeError(f"No image bytes in response. Keys: {list(data.keys())}")
    return base64.b64decode(b64)


def gen_openai_png(
    openai_api_key: str, model_name: str, prompt: str, size: str
) -> bytes:
    """Generate a single PNG via OpenAI Images API.

    Handles both return shapes:
    - gpt-image-1: `data[0].b64_json` (base64-encoded)
    - dall-e-3: `data[0].url` (download the URL)
    """
    openai.api_key = openai_api_key

    size_lit: OpenAIImageSize = cast(OpenAIImageSize, size)

    result: Any = openai.images.generate(model=model_name, prompt=prompt, size=size_lit)

    data_list: Any = getattr(result, "data", None)
    if not data_list:
        raise RuntimeError("No image data returned from OpenAI Images API")

    first: Any = data_list[0]

    b64_json: Optional[str] = getattr(first, "b64_json", None)
    if b64_json:
        return base64.b64decode(b64_json)

    url_val: Optional[str] = getattr(first, "url", None)
    if url_val:
        resp = requests.get(url_val, timeout=120)
        resp.raise_for_status()
        return resp.content

    raise RuntimeError("No usable image field (`b64_json` or `url`) in OpenAI response")


def gen_grok_png(
    api_key: str, model_name: str, prompt: str, image_format: str
) -> bytes:
    """Generate a PNG via xAI Grok Images API (single attempt)."""
    url = "https://api.x.ai/v1/images/generations"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model_name,
        "prompt": prompt,
        "response_format": image_format,
        "n": 1,
    }

    r = requests.post(url, headers=headers, json=payload, timeout=120)
    r.raise_for_status()
    data = r.json()

    if "data" in data and data["data"]:
        img_url = data["data"][0]["url"]
        rr = requests.get(img_url, timeout=120)
        rr.raise_for_status()
        return rr.content
    raise RuntimeError("No image data in response")
