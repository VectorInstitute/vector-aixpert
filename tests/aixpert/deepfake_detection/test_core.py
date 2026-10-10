"""Unit tests for the lightweight FACT-HO domain helpers."""

from __future__ import annotations

from aixpert.deepfake_detection.core import (
    FactHOSample,
    assign_group_indices,
    assign_source_disjoint_splits,
    build_bundles_from_samples,
    infer_fakeav_modality_labels,
    infer_vcapav_content_bucket,
    rebalance_train_samples_by_method,
)


def make_sample(
    sample_id: str, source: str, split: str, label_a: int, label_v: int
) -> FactHOSample:
    """Build a compact sample fixture."""
    return FactHOSample(
        sample_id=sample_id,
        dataset_name="fakeavceleb",
        split=split,
        bundle_id=source,
        content_family="face_demo",
        video_path=f"/tmp/{sample_id}.mp4",
        audio_path=f"/tmp/{sample_id}.wav",
        label_y=1 if (label_a or label_v) else 0,
        label_a=label_a,
        label_v=label_v,
        method="demo",
        source=source,
    )


def test_build_bundles_and_group_indices() -> None:
    """Bundles should be deterministic and receive stable group indices."""
    samples = [
        make_sample("one", "clip_a", "train", 0, 0),
        make_sample("two", "clip_a", "train", 1, 0),
        make_sample("three", "clip_b", "train", 0, 0),
    ]
    bundles = build_bundles_from_samples(samples)

    assert [bundle.bundle_id for bundle in bundles] == ["clip_a", "clip_b"]
    assert bundles[0].pattern_signature == "FR+RR"

    group_names = assign_group_indices(bundles)
    assert len(group_names) == 2
    assert bundles[0].group_index >= 0
    assert bundles[1].group_index >= 0


def test_assign_source_disjoint_splits() -> None:
    """Source-disjoint assignment should cover all requested split names."""
    samples = [
        make_sample("a1", "source_a", "unknown", 0, 0),
        make_sample("b1", "source_b", "unknown", 0, 0),
        make_sample("c1", "source_c", "unknown", 1, 0),
    ]

    assign_source_disjoint_splits(
        samples, "train", "dev", "test", 0.6, 0.2, 0.2, seed=7
    )

    splits = {sample.split for sample in samples}
    assert splits == {"train", "dev", "test"}


def test_rebalance_train_samples_by_method() -> None:
    """Method-aware rebalancing should reduce excessive fake skew."""
    train_samples = [
        make_sample("real", "r", "train", 0, 0),
        make_sample("fake_1", "f1", "train", 1, 0),
        make_sample("fake_2", "f2", "train", 1, 0),
        make_sample("fake_3", "f3", "train", 0, 1),
    ]
    train_samples[1].method = "audio_a"
    train_samples[2].method = "audio_b"
    train_samples[3].method = "video_a"

    balanced = rebalance_train_samples_by_method(
        train_samples, max_fake_real_ratio=1.0, seed=3
    )

    num_fake = sum(sample.label_y for sample in balanced)
    assert len(balanced) == 2
    assert num_fake == 1


def test_infer_fakeav_modality_labels() -> None:
    """Metadata labels should map to the expected modality supervision."""
    assert infer_fakeav_modality_labels("RealVideo-RealAudio", "", "") == (0, 0)
    assert infer_fakeav_modality_labels("", "B", "") == (1, 0)
    assert infer_fakeav_modality_labels("", "C", "") == (0, 1)
    assert infer_fakeav_modality_labels("", "D", "") == (1, 1)


def test_infer_vcapav_content_bucket_is_deterministic() -> None:
    """Content buckets should stay stable for a fixed source string."""
    bucket_a = infer_vcapav_content_bucket("clip_001", num_buckets=8)
    bucket_b = infer_vcapav_content_bucket("clip_001", num_buckets=8)

    assert bucket_a == bucket_b
    assert bucket_a.startswith("environment_bucket_")
