#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Sample and convert Jigsaw dataset from Kaggle CSV to Parquet.

The script converts the Jigsaw Unintended Bias dataset
(from manually downloaded Kaggle CSV) into a smaller Parquet file.

Usage:
  python scripts/sample_jigsaw.py --data_dir data/jigsaw_raw
      --out data/jigsaw_sample.parquet --sample 50000
"""

import argparse
from pathlib import Path

import pandas as pd


def main() -> None:
    """Sample and convert the Jigsaw dataset to Parquet format."""
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--data_dir", required=True, help="Folder with Kaggle Jigsaw CSV (train.csv)"
    )
    ap.add_argument(
        "--data_file", default="train.csv", help="Name of the Kaggle Jigsaw CSV file"
    )
    ap.add_argument("--out", required=True, help="Output Parquet/CSV file path")
    ap.add_argument(
        "--sample", type=int, default=50000, help="Number of samples to keep"
    )
    args = ap.parse_args()

    train_path = Path(args.data_dir) / args.data_file
    if not train_path.exists():
        raise FileNotFoundError(
            f"{train_path} not found. Make sure you downloaded it from Kaggle."
        )

    print(f"Loading {train_path} ...")
    df = pd.read_csv(train_path, low_memory=False)
    print(f"Loaded {len(df):,} rows.")

    # Keep main text + identity columns
    keep_cols = [
        "comment_text",
        "target",
        "male",
        "female",
        "black",
        "white",
        "muslim",
        "jewish",
        "christian",
        "transgender",
        "homosexual_gay_or_lesbian",
    ]
    keep_cols = [c for c in keep_cols if c in df.columns]
    df = df[keep_cols]

    if args.sample < len(df):
        df = df.sample(args.sample, random_state=42)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    if args.out.endswith(".parquet"):
        df.to_parquet(args.out, index=False)
    else:
        df.to_csv(args.out, index=False)

    print(f"✅ Saved {len(df):,} rows → {args.out}")


if __name__ == "__main__":
    main()
