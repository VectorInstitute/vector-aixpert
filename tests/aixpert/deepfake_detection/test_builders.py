"""Unit tests for the curated dataset builders."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from aixpert.deepfake_detection.builders import (
    FakeAVCelebBuilder,
    FakeAVCelebConfig,
    LAVDFBuilder,
    LAVDFConfig,
    SplitConfig,
    VCapAVBuilder,
    VCapAVConfig,
)


def test_lavdf_builder_loads_counterfactual_pairs(media_root: Path) -> None:
    """LAV-DF builder should create pairwise train bundles when possible."""
    video_dir = media_root / "lavdf"
    video_dir.mkdir()
    (video_dir / "clip_real.mp4").write_text("", encoding="utf-8")
    (video_dir / "clip_fake.mp4").write_text("", encoding="utf-8")

    metadata_path = media_root / "lavdf_metadata.json"
    metadata_path.write_text(
        json.dumps(
            [
                {
                    "file": "lavdf/clip_real.mp4",
                    "split": "train",
                    "original": "source_1",
                    "n_fakes": 0,
                    "modify_audio": False,
                    "modify_video": False,
                    "duration": 3.0,
                },
                {
                    "file": "lavdf/clip_fake.mp4",
                    "split": "train",
                    "original": "source_1",
                    "n_fakes": 1,
                    "modify_audio": True,
                    "modify_video": False,
                    "duration": 3.0,
                },
            ]
        ),
        encoding="utf-8",
    )

    builder = LAVDFBuilder(
        LAVDFConfig(data_root=media_root, metadata_path=metadata_path)
    )
    partitions = builder.partition()

    assert partitions.summary["train_bundle_mode"] == "pairwise_counterfactual"
    assert len(partitions.train_bundles) == 1
    assert partitions.train_bundles[0].pattern_signature == "FR+RR"


def test_fakeav_builder_respects_metadata_split_strategy(media_root: Path) -> None:
    """FakeAVCeleb builder should load explicit split labels from metadata."""
    data_dir = media_root / "fakeav"
    data_dir.mkdir()
    (data_dir / "real.mp4").write_text("", encoding="utf-8")
    (data_dir / "fake.mp4").write_text("", encoding="utf-8")

    metadata_path = media_root / "fakeav.csv"
    with metadata_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "filename",
                "path",
                "path_dir",
                "type",
                "category",
                "method",
                "source",
                "race",
                "gender",
                "target1",
                "target2",
                "split",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "filename": "real.mp4",
                "path": "",
                "path_dir": "fakeav",
                "type": "RealVideo-RealAudio",
                "category": "A",
                "method": "real",
                "source": "src_a",
                "race": "Asian",
                "gender": "Female",
                "target1": "anchor_a",
                "target2": "-",
                "split": "train",
            }
        )
        writer.writerow(
            {
                "filename": "fake.mp4",
                "path": "",
                "path_dir": "fakeav",
                "type": "RealVideo-FakeAudio",
                "category": "B",
                "method": "tts_a",
                "source": "src_a",
                "race": "Asian",
                "gender": "Female",
                "target1": "anchor_a",
                "target2": "-",
                "split": "dev",
            }
        )

    builder = FakeAVCelebBuilder(
        FakeAVCelebConfig(
            data_root=media_root, metadata_path=metadata_path, split_strategy="metadata"
        )
    )
    partitions = builder.partition()

    assert partitions.summary["num_all_samples"] == 2
    assert len(partitions.train_bundles) == 1
    assert len(partitions.eval_bundles) == 1


def test_vcapav_builder_loads_manifest_first_metadata(media_root: Path) -> None:
    """VCapAV builder should support a single-sample manifest smoke test."""
    media_dir = media_root / "vcapav"
    media_dir.mkdir()
    (media_dir / "clip_001.mp4").write_text("", encoding="utf-8")
    (media_dir / "clip_001.wav").write_text("", encoding="utf-8")

    metadata_path = media_root / "vcapav_manifest.jsonl"
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

    builder = VCapAVBuilder(
        VCapAVConfig(
            data_root=media_root,
            metadata_path=metadata_path,
            split_strategy="metadata",
        ),
        split_config=SplitConfig(train="train", eval="dev", test="test"),
    )
    partitions = builder.partition()

    assert partitions.summary["num_all_samples"] == 1
    assert len(partitions.train_bundles) == 1
