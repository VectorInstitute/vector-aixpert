"""Dataset builders for a curated, testable FACT-HO preparation workflow."""

from __future__ import annotations

import csv
import json
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from aixpert.deepfake_detection.core import (
    FactHOBundle,
    FactHOSample,
    assign_group_indices,
    assign_source_disjoint_splits,
    build_bundles_from_samples,
    count_bundle_groups,
    count_bundle_patterns,
    count_dataset_bundles,
    count_dataset_samples,
    duration_bucket,
    infer_fakeav_modality_labels,
    infer_vcapav_content_bucket,
    rebalance_train_samples_by_method,
    sanitize_slug,
    select_bundles,
    select_samples_by_split,
)


@dataclass(frozen=True)
class SplitConfig:
    """Name the train/eval/test splits used across all builders."""

    train: str = "train"
    eval: str = "dev"
    test: str = "test"


@dataclass(frozen=True)
class SelectionLimits:
    """Cap how many samples or bundles are used per split."""

    max_train_bundles: int = 0
    max_eval_bundles: int = 0
    max_test_bundles: int = 0
    max_train_samples: int = 0
    max_eval_samples: int = 0
    max_test_samples: int = 0


@dataclass(frozen=True)
class LAVDFConfig:
    """Configure LAV-DF loading."""

    data_root: Path
    metadata_path: Path | None = None
    short_threshold: float = 5.0
    medium_threshold: float = 10.0


@dataclass(frozen=True)
class FakeAVCelebConfig:
    """Configure FakeAVCeleb loading."""

    data_root: Path
    metadata_path: Path | None = None
    split_strategy: str = "source"
    train_ratio: float = 0.8
    eval_ratio: float = 0.1
    test_ratio: float = 0.1
    rebalance_train: bool = True
    max_fake_real_ratio: float = 12.0


@dataclass(frozen=True)
class VCapAVConfig:
    """Configure VCapAV loading from a manifest-first interface."""

    data_root: Path
    metadata_path: Path
    split_strategy: str = "source"
    train_ratio: float = 0.8
    eval_ratio: float = 0.1
    test_ratio: float = 0.1
    rebalance_train: bool = True
    max_fake_real_ratio: float = 4.0
    content_buckets: int = 8


@dataclass
class DatasetPartitions:
    """Store per-split bundles together with an inspection summary."""

    dataset_name: str
    train_bundles: list[FactHOBundle]
    eval_bundles: list[FactHOBundle]
    test_bundles: list[FactHOBundle]
    summary: dict[str, Any] = field(default_factory=dict)

    def to_summary_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable summary payload."""
        return {
            "dataset_name": self.dataset_name,
            "num_train_bundles": len(self.train_bundles),
            "num_eval_bundles": len(self.eval_bundles),
            "num_test_bundles": len(self.test_bundles),
            **self.summary,
        }


def build_vcapav_counterfactual_bundles(samples: list[FactHOSample]) -> list[FactHOBundle]:
    """Expand VCapAV train samples into pairwise counterfactual bundles."""
    grouped: dict[tuple[str, str, str, str, str], list[FactHOSample]] = defaultdict(list)
    for sample in samples:
        key = (
            sample.bundle_id,
            sample.dataset_name,
            sample.split,
            sample.content_family,
            sample.source,
        )
        grouped[key].append(sample)

    bundles: list[FactHOBundle] = []
    for key, group_samples in grouped.items():
        bundle_id, dataset_name, split, content_family, source = key
        by_pattern: dict[tuple[int, int], list[FactHOSample]] = defaultdict(list)
        for sample in sorted(group_samples, key=lambda item: (item.pattern, item.method, item.sample_id)):
            by_pattern[(sample.label_a, sample.label_v)].append(sample)

        real_anchor = by_pattern.get((0, 0), [None])[0]
        created = False

        if real_anchor is not None:
            for suffix, pattern_key in [("af", (1, 0)), ("vf", (0, 1)), ("ff", (1, 1))]:
                for sample in by_pattern.get(pattern_key, []):
                    bundles.append(
                        FactHOBundle(
                            bundle_id=f"{bundle_id}::{suffix}::{sample.method or sample.sample_id}",
                            dataset_name=dataset_name,
                            split=split,
                            content_family=content_family,
                            source=source,
                            samples=[real_anchor, sample],
                        )
                    )
                    created = True

        if created:
            continue

        bundles.append(
            FactHOBundle(
                bundle_id=bundle_id,
                dataset_name=dataset_name,
                split=split,
                content_family=content_family,
                source=source,
                samples=sorted(group_samples, key=lambda item: (item.pattern, item.method, item.sample_id)),
            )
        )

    bundles.sort(key=lambda item: (item.dataset_name, item.split, item.bundle_id))
    return bundles


def build_lavdf_counterfactual_bundles(samples: list[FactHOSample]) -> list[FactHOBundle]:
    """Expand LAV-DF train samples into pairwise counterfactual bundles."""
    grouped: dict[tuple[str, str, str, str, str], list[FactHOSample]] = defaultdict(list)
    for sample in samples:
        key = (
            sample.bundle_id,
            sample.dataset_name,
            sample.split,
            sample.content_family,
            sample.source,
        )
        grouped[key].append(sample)

    bundles: list[FactHOBundle] = []
    for key, group_samples in grouped.items():
        bundle_id, dataset_name, split, content_family, source = key
        ordered_samples = sorted(group_samples, key=lambda item: (item.pattern, item.method, item.sample_id))
        by_pattern: dict[tuple[int, int], list[FactHOSample]] = defaultdict(list)
        for sample in ordered_samples:
            by_pattern[(sample.label_a, sample.label_v)].append(sample)

        real_anchors = by_pattern.get((0, 0), [])
        fake_specs = [
            ("af", by_pattern.get((1, 0), [])),
            ("vf", by_pattern.get((0, 1), [])),
            ("ff", by_pattern.get((1, 1), [])),
        ]

        used_anchor_indices: set[int] = set()
        created = False
        if real_anchors and any(samples_for_pattern for _, samples_for_pattern in fake_specs):
            for suffix, samples_for_pattern in fake_specs:
                for sample_idx, sample in enumerate(samples_for_pattern):
                    anchor_idx = sample_idx % len(real_anchors)
                    anchor = real_anchors[anchor_idx]
                    used_anchor_indices.add(anchor_idx)
                    bundles.append(
                        FactHOBundle(
                            bundle_id=f"{bundle_id}::{suffix}::{sample.method or sample.sample_id}",
                            dataset_name=dataset_name,
                            split=split,
                            content_family=content_family,
                            source=source,
                            samples=[anchor, sample],
                        )
                    )
                    created = True

            for anchor_idx, anchor in enumerate(real_anchors):
                if anchor_idx in used_anchor_indices:
                    continue
                bundles.append(
                    FactHOBundle(
                        bundle_id=f"{bundle_id}::rr::{anchor.method or anchor.sample_id}",
                        dataset_name=dataset_name,
                        split=split,
                        content_family=content_family,
                        source=source,
                        samples=[anchor],
                    )
                )
            if created:
                continue

        ff_anchors = by_pattern.get((1, 1), [])
        fake_only_specs = [
            ("ffv", by_pattern.get((1, 0), [])),
            ("ffa", by_pattern.get((0, 1), [])),
        ]
        used_ff_anchor_indices: set[int] = set()
        created = False
        if ff_anchors and any(samples_for_pattern for _, samples_for_pattern in fake_only_specs):
            for suffix, samples_for_pattern in fake_only_specs:
                for sample_idx, sample in enumerate(samples_for_pattern):
                    anchor_idx = sample_idx % len(ff_anchors)
                    anchor = ff_anchors[anchor_idx]
                    used_ff_anchor_indices.add(anchor_idx)
                    bundles.append(
                        FactHOBundle(
                            bundle_id=f"{bundle_id}::{suffix}::{sample.method or sample.sample_id}",
                            dataset_name=dataset_name,
                            split=split,
                            content_family=content_family,
                            source=source,
                            samples=[anchor, sample],
                        )
                    )
                    created = True

            for anchor_idx, anchor in enumerate(ff_anchors):
                if anchor_idx in used_ff_anchor_indices:
                    continue
                bundles.append(
                    FactHOBundle(
                        bundle_id=f"{bundle_id}::ff::{anchor.method or anchor.sample_id}",
                        dataset_name=dataset_name,
                        split=split,
                        content_family=content_family,
                        source=source,
                        samples=[anchor],
                    )
                )
            if created:
                continue

        bundles.append(
            FactHOBundle(
                bundle_id=bundle_id,
                dataset_name=dataset_name,
                split=split,
                content_family=content_family,
                source=source,
                samples=ordered_samples,
            )
        )

    bundles.sort(key=lambda item: (item.dataset_name, item.split, item.bundle_id))
    return bundles


class DatasetBuilder(ABC):
    """Abstract base class for dataset-specific sample and bundle builders."""

    dataset_name: str

    def __init__(self, split_config: SplitConfig | None = None, seed: int = 42) -> None:
        self.split_config = split_config or SplitConfig()
        self.seed = seed

    @abstractmethod
    def load_samples(self) -> list[FactHOSample]:
        """Load flat samples from the dataset metadata source."""

    def train_bundle_builder(self, samples: list[FactHOSample]) -> list[FactHOBundle]:
        """Build train bundles from train samples."""
        return build_bundles_from_samples(samples)

    def eval_bundle_builder(self, samples: list[FactHOSample]) -> list[FactHOBundle]:
        """Build eval bundles from eval samples."""
        return build_bundles_from_samples(samples)

    def test_bundle_builder(self, samples: list[FactHOSample]) -> list[FactHOBundle]:
        """Build test bundles from test samples."""
        return build_bundles_from_samples(samples)

    def adjust_train_samples(self, train_samples: list[FactHOSample]) -> list[FactHOSample]:
        """Optionally rebalance or prune train samples before bundling."""
        return train_samples

    def _summary(
        self,
        all_samples: list[FactHOSample],
        train_samples: list[FactHOSample],
        eval_samples: list[FactHOSample],
        test_samples: list[FactHOSample],
        train_bundles: list[FactHOBundle],
        eval_bundles: list[FactHOBundle],
        test_bundles: list[FactHOBundle],
        train_bundle_mode: str,
    ) -> dict[str, Any]:
        assign_group_indices(train_bundles)
        return {
            "dataset_name": self.dataset_name,
            "num_all_samples": len(all_samples),
            "num_train_samples": len(train_samples),
            "num_eval_samples": len(eval_samples),
            "num_test_samples": len(test_samples),
            "num_train_bundles": len(train_bundles),
            "num_eval_bundles": len(eval_bundles),
            "num_test_bundles": len(test_bundles),
            "train_bundle_mode": train_bundle_mode,
            "train_bundle_patterns": count_bundle_patterns(train_bundles),
            "eval_bundle_patterns": count_bundle_patterns(eval_bundles),
            "test_bundle_patterns": count_bundle_patterns(test_bundles),
            "train_bundle_groups": count_bundle_groups(train_bundles),
            "train_dataset_bundles": count_dataset_bundles(train_bundles),
            "train_dataset_samples": count_dataset_samples(train_samples),
            "eval_dataset_samples": count_dataset_samples(eval_samples),
            "test_dataset_samples": count_dataset_samples(test_samples),
        }

    def partition(self, limits: SelectionLimits | None = None) -> DatasetPartitions:
        """Build train/eval/test partitions together with a compact summary."""
        limits = limits or SelectionLimits()
        all_samples = self.load_samples()

        train_samples = select_samples_by_split(
            samples=all_samples,
            split=self.split_config.train,
            max_samples=limits.max_train_samples,
            seed=self.seed,
        )
        eval_samples = select_samples_by_split(
            samples=all_samples,
            split=self.split_config.eval,
            max_samples=limits.max_eval_samples,
            seed=self.seed,
        )
        test_samples = select_samples_by_split(
            samples=all_samples,
            split=self.split_config.test,
            max_samples=limits.max_test_samples,
            seed=self.seed,
        )

        train_samples = self.adjust_train_samples(train_samples)
        train_bundles = select_bundles(self.train_bundle_builder(train_samples), limits.max_train_bundles, self.seed)
        eval_bundles = select_bundles(self.eval_bundle_builder(eval_samples), limits.max_eval_bundles, self.seed)
        test_bundles = select_bundles(self.test_bundle_builder(test_samples), limits.max_test_bundles, self.seed)

        train_bundle_mode = "full"
        if type(self).train_bundle_builder is not DatasetBuilder.train_bundle_builder:
            train_bundle_mode = "pairwise_counterfactual"

        return DatasetPartitions(
            dataset_name=self.dataset_name,
            train_bundles=train_bundles,
            eval_bundles=eval_bundles,
            test_bundles=test_bundles,
            summary=self._summary(
                all_samples=all_samples,
                train_samples=train_samples,
                eval_samples=eval_samples,
                test_samples=test_samples,
                train_bundles=train_bundles,
                eval_bundles=eval_bundles,
                test_bundles=test_bundles,
                train_bundle_mode=train_bundle_mode,
            ),
        )


class LAVDFBuilder(DatasetBuilder):
    """Load and bundle LAV-DF metadata."""

    dataset_name = "lavdf"

    def __init__(self, config: LAVDFConfig, split_config: SplitConfig | None = None, seed: int = 42) -> None:
        super().__init__(split_config=split_config, seed=seed)
        self.config = config

    def load_samples(self) -> list[FactHOSample]:
        """Load LAV-DF metadata into flat FACT-HO samples."""
        metadata_path = self.config.metadata_path or (self.config.data_root / "metadata.json")
        if not metadata_path.exists():
            raise FileNotFoundError(f"LAV-DF metadata not found: {metadata_path}")

        rows = json.loads(metadata_path.read_text(encoding="utf-8"))
        samples: list[FactHOSample] = []
        for row in rows:
            rel_path = row.get("file")
            if not rel_path:
                continue
            abs_path = self.config.data_root / rel_path
            if not abs_path.exists():
                continue
            n_fakes = int(row.get("n_fakes", 0) or 0)
            audio_label = 1 if bool(row.get("modify_audio", False)) else 0
            video_label = 1 if bool(row.get("modify_video", False)) else 0
            bundle_id = str(row.get("original") or rel_path)
            duration = float(row.get("duration", 0.0) or 0.0)
            samples.append(
                FactHOSample(
                    sample_id=f"lavdf::{rel_path}",
                    dataset_name=self.dataset_name,
                    split=str(row.get("split", "unknown")),
                    bundle_id=bundle_id,
                    content_family=duration_bucket(
                        duration=duration,
                        short_threshold=self.config.short_threshold,
                        medium_threshold=self.config.medium_threshold,
                    ),
                    video_path=str(abs_path),
                    audio_path=str(abs_path),
                    label_y=1 if n_fakes > 0 else 0,
                    label_a=audio_label,
                    label_v=video_label,
                    method="lavdf",
                    source=bundle_id,
                    metadata={
                        "duration": duration,
                        "n_fakes": n_fakes,
                        "original": row.get("original"),
                    },
                )
            )
        return samples

    def train_bundle_builder(self, samples: list[FactHOSample]) -> list[FactHOBundle]:
        """Build memory-friendlier pairwise train bundles for LAV-DF."""
        return build_lavdf_counterfactual_bundles(samples)


class FakeAVCelebBuilder(DatasetBuilder):
    """Load and bundle FakeAVCeleb metadata."""

    dataset_name = "fakeavceleb"

    def __init__(self, config: FakeAVCelebConfig, split_config: SplitConfig | None = None, seed: int = 42) -> None:
        super().__init__(split_config=split_config, seed=seed)
        self.config = config

    def load_samples(self) -> list[FactHOSample]:
        """Load FakeAVCeleb metadata into flat FACT-HO samples."""
        metadata_path = self.config.metadata_path or (self.config.data_root / "meta_data.csv")
        if not metadata_path.exists():
            raise FileNotFoundError(f"FakeAVCeleb metadata not found: {metadata_path}")

        samples: list[FactHOSample] = []
        with metadata_path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for idx, row in enumerate(reader):
                raw_filename = (row.get("filename") or "").strip()
                raw_path = (row.get("path") or "").strip()
                raw_dir_extra = (row.get("path_dir") or row.get("") or "").strip()

                if raw_filename:
                    filename = raw_filename
                    rel_dir = raw_path if raw_path and not raw_path.lower().endswith(".mp4") else raw_dir_extra
                else:
                    filename = raw_path
                    rel_dir = raw_dir_extra

                if rel_dir.startswith("FakeAVCeleb/"):
                    rel_dir = rel_dir[len("FakeAVCeleb/") :]

                if not filename:
                    continue

                full_path = self.config.data_root / rel_dir / filename
                if not full_path.exists():
                    continue

                sample_type = (row.get("type") or "").strip()
                category = (row.get("category") or "").strip()
                method = (row.get("method") or "").strip()
                source = (row.get("source") or "unknown").strip()
                race = sanitize_slug(str(row.get("race", "")), "unknownrace")
                gender = sanitize_slug(str(row.get("gender", "")), "unknowngender")
                audio_label, video_label = infer_fakeav_modality_labels(sample_type, category, method)
                label_y = 1 if (audio_label == 1 or video_label == 1) else 0

                target1 = (row.get("target1") or "").strip()
                target2 = (row.get("target2") or "").strip()
                anchor_target = target1 if target1 and target1 != "-" else target2
                if not anchor_target or anchor_target == "-":
                    anchor_target = filename
                bundle_id = f"{source}::{anchor_target}"
                content_family = f"face_{race}_{gender}"

                samples.append(
                    FactHOSample(
                        sample_id=f"fakeav::{source}::{filename}::{idx}",
                        dataset_name=self.dataset_name,
                        split=(row.get("split") or "unknown").strip(),
                        bundle_id=bundle_id,
                        content_family=content_family,
                        video_path=str(full_path),
                        audio_path=str(full_path),
                        label_y=label_y,
                        label_a=audio_label,
                        label_v=video_label,
                        method=method or "unknown",
                        source=source,
                        metadata={
                            "race": race,
                            "gender": gender,
                            "category": category,
                            "sample_type": sample_type,
                        },
                    )
                )

        if self.config.split_strategy == "source":
            assign_source_disjoint_splits(
                samples=samples,
                train_split_name=self.split_config.train,
                eval_split_name=self.split_config.eval,
                test_split_name=self.split_config.test,
                train_ratio=self.config.train_ratio,
                eval_ratio=self.config.eval_ratio,
                test_ratio=self.config.test_ratio,
                seed=self.seed,
            )
        return samples

    def adjust_train_samples(self, train_samples: list[FactHOSample]) -> list[FactHOSample]:
        """Optionally rebalance fake methods in the train split."""
        if not self.config.rebalance_train:
            return train_samples
        return rebalance_train_samples_by_method(
            train_samples=train_samples,
            max_fake_real_ratio=self.config.max_fake_real_ratio,
            seed=self.seed,
        )


class VCapAVBuilder(DatasetBuilder):
    """Load and bundle VCapAV samples from a curated manifest file."""

    dataset_name = "vcapav"

    def __init__(self, config: VCapAVConfig, split_config: SplitConfig | None = None, seed: int = 42) -> None:
        super().__init__(split_config=split_config, seed=seed)
        self.config = config

    def _resolve_path(self, raw_path: str) -> str:
        path = Path(raw_path)
        if not path.is_absolute():
            path = self.config.data_root / path
        return str(path)

    def load_samples(self) -> list[FactHOSample]:
        """Load a manifest-first VCapAV view without cluster-specific zip extraction."""
        if not self.config.metadata_path.exists():
            raise FileNotFoundError(f"VCapAV metadata not found: {self.config.metadata_path}")

        samples: list[FactHOSample] = []
        with self.config.metadata_path.open("r", encoding="utf-8") as handle:
            for raw_line in handle:
                stripped_line = raw_line.strip()
                if not stripped_line:
                    continue
                row = json.loads(stripped_line)
                source = str(row.get("source") or row.get("clip_id") or row.get("bundle_id") or row.get("group_key"))
                content_family = row.get("content_family") or infer_vcapav_content_bucket(
                    source=source,
                    num_buckets=self.config.content_buckets,
                )
                samples.append(
                    FactHOSample(
                        sample_id=str(row.get("sample_id") or row.get("uid") or row.get("clip_id")),
                        dataset_name=self.dataset_name,
                        split=str(row.get("split", "unknown")),
                        bundle_id=str(row.get("bundle_id") or row.get("group_key") or row.get("clip_id")),
                        content_family=str(content_family),
                        video_path=self._resolve_path(str(row["video_path"])),
                        audio_path=self._resolve_path(str(row["audio_path"])),
                        label_y=int(row.get("label_y", row.get("label", 0))),
                        label_a=int(row.get("label_a", row.get("audio_label", 0))),
                        label_v=int(row.get("label_v", row.get("video_label", 0))),
                        method=str(row.get("method", "unknown")),
                        source=source,
                        metadata={"scenario": row.get("scenario", "")},
                    )
                )

        if self.config.split_strategy == "source":
            assign_source_disjoint_splits(
                samples=samples,
                train_split_name=self.split_config.train,
                eval_split_name=self.split_config.eval,
                test_split_name=self.split_config.test,
                train_ratio=self.config.train_ratio,
                eval_ratio=self.config.eval_ratio,
                test_ratio=self.config.test_ratio,
                seed=self.seed,
            )
        return samples

    def train_bundle_builder(self, samples: list[FactHOSample]) -> list[FactHOBundle]:
        """Build pairwise counterfactual train bundles for VCapAV."""
        return build_vcapav_counterfactual_bundles(samples)

    def adjust_train_samples(self, train_samples: list[FactHOSample]) -> list[FactHOSample]:
        """Optionally rebalance fake methods in the train split."""
        if not self.config.rebalance_train:
            return train_samples
        return rebalance_train_samples_by_method(
            train_samples=train_samples,
            max_fake_real_ratio=self.config.max_fake_real_ratio,
            seed=self.seed,
        )
