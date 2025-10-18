#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Download and normalize social-problem datasets into Parquet files.

Supported datasets:
- Jigsaw Unintended Bias (HF: google/jigsaw_unintended_bias)
- CivilComments (HF: google/civil_comments)
- CivilComments-WILDS (HF mirror: shlomihod/civil-comments-wilds)
- SBIC / Social Bias Frames (HF: allenai/social_bias_frames)
- HateXplain (HF: Hate-speech-CNERG/hatexplain)

Examples of usage:
1. Download a sample of 50,000 rows from the Jigsaw dataset:
   python scripts/download_data.py --dataset jigsaw
       --out data/jigsaw.parquet --sample 50000

2. Stream and take 200,000 rows from the CivilComments dataset:
   python scripts/download_data.py --dataset civil
       --out data/civil.parquet --stream --take 200000

3. Stream and take 500 rows from the CivilComments dataset:
   uv run scripts/download_data.py --dataset civil
       --out data/civil.parquet --stream --take 500

Note:
- The Jigsaw dataset requires Kaggle credentials for downloading
  and extracting the data. This can be handled later.
"""

# Importing necessary libraries
import argparse  # For parsing command-line arguments
import itertools
import random
from collections.abc import Generator
from pathlib import Path  # For working with file paths
from typing import Any, Iterator

import pandas as pd  # For data manipulation and analysis
from datasets import (  # For loading datasets from Hugging Face
    load_dataset,
)


# Utility function to convert a value to a boolean
def as_bool(x: Any) -> bool:
    """Convert a value to a boolean."""
    return str(x).lower() in {"1", "true", "t", "yes", "y"}


# Function to save a DataFrame to a Parquet file
def to_parquet(df: pd.DataFrame, out_path: str) -> None:
    """Save a DataFrame to a Parquet file."""
    out_path_obj = Path(out_path)  # Convert the output path to a Path object
    out_path_obj.parent.mkdir(
        parents=True, exist_ok=True
    )  # Create parent directories if they don't exist
    df.to_parquet(out_path_obj, index=False)  # Save the DataFrame as a Parquet file
    print(
        f"Wrote {len(df):,} rows -> {out_path_obj}"
    )  # Print the number of rows written


# Function to perform reservoir sampling on an iterable
def sample_iter(it: Iterator[Any], n: int) -> list[Any]:
    """Perform reservoir sampling on an iterable."""
    out: list[Any] = []  # Initialize the output list
    for seen, row in enumerate(it, start=1):
        if len(out) < n:
            out.append(
                row
            )  # Add the row to the output if the output size is less than n
        else:
            j = random.randint(0, seen - 1)  # Randomly replace an existing element
            if j < n:
                out[j] = row
    return out


# Function to load the Jigsaw dataset
def load_jigsaw(
    stream: bool = False, take: int | None = None, split: str = "train"
) -> pd.DataFrame:
    """Load the Jigsaw Unintended Bias dataset."""
    ds = load_dataset(
        "google/jigsaw_unintended_bias",
        split=split,
        streaming=stream,
        trust_remote_code=True,
    )
    cols_keep = [
        "comment_text",
        "target",
        "severe_toxicity",
        "obscene",
        "identity_attack",
        "insult",
        "threat",
        "male",
        "female",
        "transgender",
        "other_gender",
        "heterosexual",
        "homosexual_gay_or_lesbian",
        "bisexual",
        "other_sexual_orientation",
        "christian",
        "jewish",
        "muslim",
        "hindu",
        "buddhist",
        "atheist",
        "other_religion",
        "black",
        "white",
        "asian",
        "latino",
        "other_race_or_ethnicity",
    ]
    if stream:
        # Stream the dataset and filter columns
        it_gen: Generator[dict[str, Any], None, None] = (
            {
                "comment_text": r.get("comment_text", ""),
                "target": r.get("target", None),
                "severe_toxicity": r.get("severe_toxicity", None),
                "obscene": r.get("obscene", None),
                "identity_attack": r.get("identity_attack", None),
                "insult": r.get("insult", None),
                "threat": r.get("threat", None),
                **{c: r.get(c, None) for c in cols_keep[7:]},
            }
            for r in ds
        )
        it = list(itertools.islice(it_gen, int(take))) if take else list(it_gen)
        return pd.DataFrame(it)  # Convert to a DataFrame
    # Remove unwanted columns and convert to a DataFrame
    ds = ds.remove_columns([c for c in ds.column_names if c not in cols_keep])
    return ds.to_pandas()


# Function to load the CivilComments dataset
def load_civil(
    stream: bool = False, take: int | None = None, split: str = "train"
) -> pd.DataFrame:
    """Load the CivilComments dataset."""
    ds = load_dataset(
        "google/civil_comments", split=split, streaming=stream, trust_remote_code=True
    )
    cols_keep = [
        "text",
        "toxicity",
        "severe_toxicity",
        "obscene",
        "identity_attack",
        "insult",
        "threat",
    ]
    if stream:
        it_gen: Generator[dict[str, Any], None, None] = (
            {
                "comment_text": r.get("text", ""),
                "target": r.get("toxicity", None),
                "severe_toxicity": r.get("severe_toxicity", None),
                "obscene": r.get("obscene", None),
                "identity_attack": r.get("identity_attack", None),
                "insult": r.get("insult", None),
                "threat": r.get("threat", None),
            }
            for r in ds
        )
        it = list(itertools.islice(it_gen, int(take))) if take else list(it_gen)
        return pd.DataFrame(it)  # Convert to a DataFrame
    # Remove unwanted columns and rename for consistency
    ds = ds.remove_columns([c for c in ds.column_names if c not in cols_keep])
    return ds.to_pandas().rename(columns={"text": "comment_text", "toxicity": "target"})


# Function to load the CivilComments-WILDS dataset
def load_wilds(
    stream: bool = False, take: int | None = None, split: str = "train"
) -> pd.DataFrame:
    """Load the CivilComments-WILDS dataset."""
    ds = load_dataset(
        "shlomihod/civil-comments-wilds",
        split=split,
        streaming=stream,
        trust_remote_code=True,
    )
    if stream:
        it_gen: Generator[dict[str, Any], None, None] = (
            {"comment_text": r.get("text", ""), "target": r.get("toxicity", None)}
            for r in ds
        )
        it = list(itertools.islice(it_gen, int(take))) if take else list(it_gen)
        return pd.DataFrame(it)  # Convert to a DataFrame
    cols = ["text", "toxicity"]
    ds = ds.remove_columns([c for c in ds.column_names if c not in cols])
    return ds.to_pandas().rename(columns={"text": "comment_text", "toxicity": "target"})


# Function to load the SBIC dataset
def load_sbic(
    stream: bool = False, take: int | None = None, split: str = "train"
) -> pd.DataFrame:
    """Load the SBIC (Social Bias Frames) dataset."""
    ds = load_dataset(
        "allenai/social_bias_frames",
        split=split,
        streaming=stream,
        trust_remote_code=True,
    )
    keep = [
        "post",
        "targetStereotype",
        "offenseScore",
        "annotators",
    ]  # Minimal fields to keep
    if stream:
        it_gen: Generator[dict[str, Any], None, None] = (
            {
                "comment_text": r.get("post", ""),
                "target": 1
                if (r.get("offenseScore", 0) and r["offenseScore"] >= 0.5)
                else 0,
                "meta": str({k: r.get(k, None) for k in keep[1:]}),
            }
            for r in ds
        )
        it = list(itertools.islice(it_gen, int(take))) if take else list(it_gen)
        return pd.DataFrame(it)  # Convert to a DataFrame
    ds = ds.remove_columns([c for c in ds.column_names if c not in keep])
    df = ds.to_pandas().rename(columns={"post": "comment_text"})
    df["target"] = (df["offenseScore"].fillna(0) >= 0.5).astype(int)  # Binarize target
    return df[["comment_text", "target"]]


# Function to load the HateXplain dataset
def load_hatexplain(
    stream: bool = False, take: int | None = None, split: str = "train"
) -> pd.DataFrame:
    """Load the HateXplain dataset."""
    ds = load_dataset(
        "Hate-speech-CNERG/hatexplain",
        split=split,
        streaming=stream,
        trust_remote_code=True,
    )
    if stream:
        it_gen: Generator[dict[str, Any], None, None] = (
            {"comment_text": " ".join(r.get("text", [])), "label": r.get("label", None)}
            for r in ds
        )
        it = list(itertools.islice(it_gen, int(take))) if take else list(it_gen)
        df = pd.DataFrame(it)  # Convert to a DataFrame
    else:
        df = ds.to_pandas()
        df["comment_text"] = df["text"].apply(
            lambda x: " ".join(x) if isinstance(x, list) else str(x)
        )
    df["target"] = df["label"].apply(
        lambda z: 1 if z in (1, 2) else 0
    )  # Binarize target
    return df[["comment_text", "target"]]


# Main function to handle command-line arguments and process datasets
def main() -> None:
    """Handle command-line arguments and process datasets."""
    ap = argparse.ArgumentParser()  # Create an argument parser
    ap.add_argument(
        "--dataset",
        required=True,
        choices=["jigsaw", "civil", "wilds", "sbic", "hatexplain"],
    )
    ap.add_argument("--out", required=True)  # Output file path
    ap.add_argument(
        "--stream", action="store_true", help="Use streaming mode (good for huge data)."
    )
    ap.add_argument(
        "--take",
        type=int,
        default=None,
        help="With --stream, cap the number of rows to read.",
    )
    ap.add_argument(
        "--sample", type=int, default=None, help="Downsample to N rows after load."
    )
    args = ap.parse_args()  # Parse command-line arguments

    # Load the appropriate dataset based on the argument
    if args.dataset == "jigsaw":
        df = load_jigsaw(stream=args.stream, take=args.take)
    elif args.dataset == "civil":
        df = load_civil(stream=args.stream, take=args.take)
    elif args.dataset == "wilds":
        df = load_wilds(stream=args.stream, take=args.take)
    elif args.dataset == "sbic":
        df = load_sbic(stream=args.stream, take=args.take)
    elif args.dataset == "hatexplain":
        df = load_hatexplain(stream=args.stream, take=args.take)
    else:
        raise ValueError("unknown dataset")

    # Downsample the dataset if requested
    if args.sample and len(df) > args.sample:
        df = df.sample(args.sample, random_state=42).reset_index(drop=True)

    # Save the dataset to a Parquet file
    to_parquet(df, args.out)


# Entry point of the script
if __name__ == "__main__":
    main()
