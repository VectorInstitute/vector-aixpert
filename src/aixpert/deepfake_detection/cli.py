"""Command-line entrypoints for curated dataset preparation workflows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from aixpert.deepfake_detection.builders import (
    FakeAVCelebBuilder,
    FakeAVCelebConfig,
    LAVDFBuilder,
    LAVDFConfig,
    SelectionLimits,
    SplitConfig,
    VCapAVBuilder,
    VCapAVConfig,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level CLI parser."""
    parser = argparse.ArgumentParser(
        description="Curated FACT-HO dataset summary helpers."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    summarize = subparsers.add_parser(
        "summarize", help="Build bundles and print a JSON summary."
    )
    summarize.add_argument(
        "--dataset", choices=["lavdf", "fakeavceleb", "vcapav"], required=True
    )
    summarize.add_argument("--data-root", type=Path, required=True)
    summarize.add_argument("--metadata-path", type=Path, default=None)
    summarize.add_argument("--output-path", type=Path, default=None)
    summarize.add_argument("--seed", type=int, default=42)
    summarize.add_argument("--train-split", default="train")
    summarize.add_argument("--eval-split", default="dev")
    summarize.add_argument("--test-split", default="test")
    summarize.add_argument("--max-train-bundles", type=int, default=0)
    summarize.add_argument("--max-eval-bundles", type=int, default=0)
    summarize.add_argument("--max-test-bundles", type=int, default=0)
    summarize.add_argument("--max-train-samples", type=int, default=0)
    summarize.add_argument("--max-eval-samples", type=int, default=0)
    summarize.add_argument("--max-test-samples", type=int, default=0)
    summarize.add_argument("--lavdf-short-threshold", type=float, default=5.0)
    summarize.add_argument("--lavdf-medium-threshold", type=float, default=10.0)
    summarize.add_argument(
        "--fakeav-split-strategy", choices=["source", "metadata"], default="source"
    )
    summarize.add_argument("--fakeav-train-ratio", type=float, default=0.8)
    summarize.add_argument("--fakeav-eval-ratio", type=float, default=0.1)
    summarize.add_argument("--fakeav-test-ratio", type=float, default=0.1)
    summarize.add_argument("--fakeav-max-fake-real-ratio", type=float, default=12.0)
    summarize.add_argument("--fakeav-no-rebalance-train", action="store_true")
    summarize.add_argument(
        "--vcapav-split-strategy", choices=["source", "metadata"], default="source"
    )
    summarize.add_argument("--vcapav-train-ratio", type=float, default=0.8)
    summarize.add_argument("--vcapav-eval-ratio", type=float, default=0.1)
    summarize.add_argument("--vcapav-test-ratio", type=float, default=0.1)
    summarize.add_argument("--vcapav-max-fake-real-ratio", type=float, default=4.0)
    summarize.add_argument("--vcapav-content-buckets", type=int, default=8)
    summarize.add_argument("--vcapav-no-rebalance-train", action="store_true")
    return parser


def make_builder(args: argparse.Namespace) -> Any:
    """Instantiate the dataset builder requested by the CLI."""
    split_config = SplitConfig(
        train=args.train_split, eval=args.eval_split, test=args.test_split
    )
    if args.dataset == "lavdf":
        return LAVDFBuilder(
            config=LAVDFConfig(
                data_root=args.data_root,
                metadata_path=args.metadata_path,
                short_threshold=args.lavdf_short_threshold,
                medium_threshold=args.lavdf_medium_threshold,
            ),
            split_config=split_config,
            seed=args.seed,
        )
    if args.dataset == "fakeavceleb":
        return FakeAVCelebBuilder(
            config=FakeAVCelebConfig(
                data_root=args.data_root,
                metadata_path=args.metadata_path,
                split_strategy=args.fakeav_split_strategy,
                train_ratio=args.fakeav_train_ratio,
                eval_ratio=args.fakeav_eval_ratio,
                test_ratio=args.fakeav_test_ratio,
                rebalance_train=not args.fakeav_no_rebalance_train,
                max_fake_real_ratio=args.fakeav_max_fake_real_ratio,
            ),
            split_config=split_config,
            seed=args.seed,
        )
    return VCapAVBuilder(
        config=VCapAVConfig(
            data_root=args.data_root,
            metadata_path=args.metadata_path
            or args.data_root / "vcapav_manifest.jsonl",
            split_strategy=args.vcapav_split_strategy,
            train_ratio=args.vcapav_train_ratio,
            eval_ratio=args.vcapav_eval_ratio,
            test_ratio=args.vcapav_test_ratio,
            rebalance_train=not args.vcapav_no_rebalance_train,
            max_fake_real_ratio=args.vcapav_max_fake_real_ratio,
            content_buckets=args.vcapav_content_buckets,
        ),
        split_config=split_config,
        seed=args.seed,
    )


def summarize_command(args: argparse.Namespace) -> dict[str, Any]:
    """Build bundles for one dataset and return the JSON summary payload."""
    builder = make_builder(args)
    partitions = builder.partition(
        SelectionLimits(
            max_train_bundles=args.max_train_bundles,
            max_eval_bundles=args.max_eval_bundles,
            max_test_bundles=args.max_test_bundles,
            max_train_samples=args.max_train_samples,
            max_eval_samples=args.max_eval_samples,
            max_test_samples=args.max_test_samples,
        )
    )
    return partitions.to_summary_dict()


def main() -> None:
    """Run the CLI."""
    parser = build_parser()
    args = parser.parse_args()
    payload = summarize_command(args)
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.output_path is not None:
        args.output_path.parent.mkdir(parents=True, exist_ok=True)
        args.output_path.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
