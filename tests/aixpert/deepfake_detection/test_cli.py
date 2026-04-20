"""Smoke tests for the command-line interface."""

from __future__ import annotations

import json
from pathlib import Path

from aixpert.deepfake_detection.cli import build_parser, summarize_command


def test_cli_summarize_supports_one_sample_vcapav_manifest(media_root: Path) -> None:
    """The CLI should produce a JSON summary from a one-sample manifest."""
    media_dir = media_root / "vcapav"
    media_dir.mkdir()
    (media_dir / "clip_001.mp4").write_text("", encoding="utf-8")
    (media_dir / "clip_001.wav").write_text("", encoding="utf-8")

    metadata_path = media_root / "smoke_manifest.jsonl"
    metadata_path.write_text(
        json.dumps(
            {
                "sample_id": "clip_001",
                "clip_id": "clip_001",
                "bundle_id": "clip_001",
                "split": "train",
                "video_path": "vcapav/clip_001.mp4",
                "audio_path": "vcapav/clip_001.wav",
                "label_y": 0,
                "label_a": 0,
                "label_v": 0,
                "method": "real",
                "source": "scene_001",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    parser = build_parser()
    args = parser.parse_args(
        [
            "summarize",
            "--dataset",
            "vcapav",
            "--data-root",
            str(media_root),
            "--metadata-path",
            str(metadata_path),
            "--vcapav-split-strategy",
            "metadata",
        ]
    )
    payload = summarize_command(args)

    assert payload["dataset_name"] == "vcapav"
    assert payload["num_all_samples"] == 1
    assert payload["num_train_bundles"] == 1
