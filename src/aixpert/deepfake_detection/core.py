"""Core domain objects and reusable helpers for FACT-HO bundle preparation."""

from __future__ import annotations

import hashlib
import random
import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class FactHOSample:
    """Represent one multimodal sample with overall and modality-specific labels."""

    sample_id: str
    dataset_name: str
    split: str
    bundle_id: str
    content_family: str
    video_path: str
    audio_path: str
    label_y: int
    label_a: int
    label_v: int
    method: str = ""
    source: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def pattern(self) -> str:
        """Return the compact audio/video supervision signature for this sample."""
        return f"{'F' if self.label_a else 'R'}{'F' if self.label_v else 'R'}"


@dataclass
class FactHOBundle:
    """Group counterfactual samples that share source content and split membership."""

    bundle_id: str
    dataset_name: str
    split: str
    content_family: str
    source: str
    samples: list[FactHOSample]
    group_name: str = ""
    group_index: int = -1

    @property
    def pattern_signature(self) -> str:
        """Summarize which audio/video label combinations appear in the bundle."""
        values = sorted({sample.pattern for sample in self.samples})
        return "+".join(values)


def count_binary(values: list[int]) -> tuple[int, int]:
    """Count positive and negative labels in a binary sequence."""
    pos = int(sum(int(value) for value in values))
    neg = len(values) - pos
    return pos, neg


def build_content_group_name(bundle: FactHOBundle) -> str:
    """Build the stable group identifier used for robust bundle grouping."""
    signature = bundle.pattern_signature or "unknown"
    return f"{bundle.dataset_name}|{bundle.content_family}|{signature}"


def assign_group_indices(bundles: list[FactHOBundle]) -> list[str]:
    """Assign stable integer group ids to bundles based on dataset/content signature."""
    group_names = sorted({build_content_group_name(bundle) for bundle in bundles})
    mapping = {name: idx for idx, name in enumerate(group_names)}
    for bundle in bundles:
        bundle.group_name = build_content_group_name(bundle)
        bundle.group_index = mapping[bundle.group_name]
    return group_names


def build_bundles_from_samples(samples: list[FactHOSample]) -> list[FactHOBundle]:
    """Group flat samples into deterministic FACT-HO bundles."""
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
    for key, bundle_samples in grouped.items():
        bundle_id, dataset_name, split, content_family, source = key
        ordered_samples = sorted(bundle_samples, key=lambda item: (item.pattern, item.method, item.sample_id))
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


def count_bundle_patterns(bundles: list[FactHOBundle]) -> dict[str, int]:
    """Count bundle pattern signatures for one partition."""
    counts: dict[str, int] = defaultdict(int)
    for bundle in bundles:
        counts[bundle.pattern_signature] += 1
    return dict(sorted(counts.items()))


def count_bundle_groups(bundles: list[FactHOBundle]) -> dict[str, int]:
    """Count bundles per robust-group identifier."""
    counts: dict[str, int] = defaultdict(int)
    for bundle in bundles:
        key = bundle.group_name or build_content_group_name(bundle)
        counts[key] += 1
    return dict(sorted(counts.items()))


def count_dataset_bundles(bundles: list[FactHOBundle]) -> dict[str, int]:
    """Count bundles per dataset."""
    counts: dict[str, int] = defaultdict(int)
    for bundle in bundles:
        counts[bundle.dataset_name] += 1
    return dict(sorted(counts.items()))


def count_dataset_samples(samples: list[FactHOSample]) -> dict[str, int]:
    """Count samples per dataset."""
    counts: dict[str, int] = defaultdict(int)
    for sample in samples:
        counts[sample.dataset_name] += 1
    return dict(sorted(counts.items()))


def normalize_ratio(train_ratio: float, eval_ratio: float, test_ratio: float) -> tuple[float, float, float]:
    """Normalize split ratios so they sum to one."""
    total = train_ratio + eval_ratio + test_ratio
    if total <= 0:
        raise ValueError("train/eval/test ratios must sum to a positive number.")
    return train_ratio / total, eval_ratio / total, test_ratio / total


def assign_source_disjoint_splits(
    samples: list[FactHOSample],
    train_split_name: str,
    eval_split_name: str,
    test_split_name: str,
    train_ratio: float,
    eval_ratio: float,
    test_ratio: float,
    seed: int,
) -> None:
    """Assign source-disjoint train/eval/test splits in place."""
    train_ratio, eval_ratio, test_ratio = normalize_ratio(train_ratio, eval_ratio, test_ratio)
    source_ids = sorted({sample.source for sample in samples})
    if len(source_ids) < 3:
        raise RuntimeError(f"Need at least 3 unique source IDs for source-disjoint split, got {len(source_ids)}.")

    rng = random.Random(seed)
    rng.shuffle(source_ids)
    n_sources = len(source_ids)

    n_train = max(1, int(round(n_sources * train_ratio)))
    n_eval = max(1, int(round(n_sources * eval_ratio)))
    n_test = max(1, n_sources - n_train - n_eval)
    if n_train + n_eval + n_test > n_sources:
        overflow = n_train + n_eval + n_test - n_sources
        n_train = max(1, n_train - overflow)

    if n_sources - (n_train + n_eval) <= 0:
        n_test = 1
        if n_train > n_eval:
            n_train -= 1
        else:
            n_eval -= 1

    train_sources = set(source_ids[:n_train])
    eval_sources = set(source_ids[n_train : n_train + n_eval])
    test_sources = set(source_ids[n_train + n_eval :])
    if not test_sources:
        test_sources.add(source_ids[-1])
        train_sources.discard(source_ids[-1])

    for sample in samples:
        if sample.source in train_sources:
            sample.split = train_split_name
        elif sample.source in eval_sources:
            sample.split = eval_split_name
        else:
            sample.split = test_split_name


def sanitize_slug(raw: str, default: str) -> str:
    """Normalize free-form text into a lowercase slug."""
    text = re.sub(r"[^a-z0-9]+", "_", (raw or "").strip().lower()).strip("_")
    return text or default


def duration_bucket(duration: float, short_threshold: float, medium_threshold: float) -> str:
    """Map clip duration to a stable content bucket label."""
    if duration <= short_threshold:
        return "face_short"
    if duration <= medium_threshold:
        return "face_medium"
    return "face_long"


def select_samples_by_split(samples: list[FactHOSample], split: str, max_samples: int, seed: int) -> list[FactHOSample]:
    """Filter one split and optionally cap the sample count."""
    subset = [sample for sample in samples if sample.split == split]
    rng = random.Random(seed)
    rng.shuffle(subset)
    if max_samples > 0:
        subset = subset[:max_samples]
    return subset


def select_bundles(bundles: list[FactHOBundle], max_bundles: int, seed: int) -> list[FactHOBundle]:
    """Optionally subsample bundles with a deterministic shuffle."""
    rng = random.Random(seed)
    shuffled = list(bundles)
    rng.shuffle(shuffled)
    if max_bundles > 0:
        shuffled = shuffled[:max_bundles]
    shuffled.sort(key=lambda bundle: (bundle.dataset_name, bundle.bundle_id))
    return shuffled


def rebalance_train_samples_by_method(
    train_samples: list[FactHOSample],
    max_fake_real_ratio: float,
    seed: int,
) -> list[FactHOSample]:
    """Downsample fake methods so train skew stays within a target ratio."""
    if max_fake_real_ratio <= 0:
        return train_samples

    real_samples = [sample for sample in train_samples if sample.label_y == 0]
    fake_samples = [sample for sample in train_samples if sample.label_y == 1]
    if not real_samples or not fake_samples:
        return train_samples

    target_fake = int(round(len(real_samples) * max_fake_real_ratio))
    target_fake = min(target_fake, len(fake_samples))
    if target_fake >= len(fake_samples):
        return train_samples

    rng = random.Random(seed)
    by_method: dict[str, list[FactHOSample]] = defaultdict(list)
    for sample in fake_samples:
        by_method[sample.method or "unknown"].append(sample)
    for values in by_method.values():
        rng.shuffle(values)

    keys = list(by_method.keys())
    rng.shuffle(keys)
    selected_fake: list[FactHOSample] = []
    cursor = 0
    while len(selected_fake) < target_fake and keys:
        key = keys[cursor % len(keys)]
        bucket = by_method[key]
        if bucket:
            selected_fake.append(bucket.pop())
            cursor += 1
            continue
        keys = [item for item in keys if by_method[item]]
        if not keys:
            break

    merged = list(real_samples) + selected_fake
    rng.shuffle(merged)
    return merged


def infer_fakeav_modality_labels(sample_type: str, category: str, method: str) -> tuple[int, int]:
    """Infer audio/video fake labels from FakeAVCeleb metadata fields."""
    sample_type_l = (sample_type or "").strip().lower()
    category_u = (category or "").strip().upper()
    method_l = (method or "").strip().lower()

    if sample_type_l == "realvideo-realaudio" or category_u == "A":
        return 0, 0
    if sample_type_l == "realvideo-fakeaudio" or category_u == "B":
        return 1, 0
    if sample_type_l == "fakevideo-realaudio" or category_u == "C":
        return 0, 1
    if sample_type_l == "fakevideo-fakeaudio" or category_u == "D":
        return 1, 1
    if method_l == "real":
        return 0, 0
    return 1, 1


def infer_vcapav_content_bucket(source: str, num_buckets: int) -> str:
    """Bucket VCapAV content sources into stable pseudo-content families."""
    if num_buckets <= 1:
        return "environment_bucket_0"
    digest = hashlib.md5(str(source).encode("utf-8")).hexdigest()
    value = int(digest[:8], 16) % num_buckets
    return f"environment_bucket_{value}"
