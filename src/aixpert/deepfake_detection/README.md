# Deepfake Detection

This module packages the most reviewable and reusable parts of the current
multimodal deepfake work into the `vector-aixpert` monorepo.

## Scope

The first version focuses on data preparation rather than full training:

- FACT-HO sample and bundle domain objects
- deterministic grouping and split helpers
- dataset builders for `LAV-DF`, `FakeAVCeleb`, and manifest-first `VCapAV`
- a small CLI for one-sample smoke summaries

## Why this is curated

The original working directory contains many experiment scripts, environment
fixes, and cluster-specific launchers. For a first monorepo integration, this
module keeps only the parts that are easiest to review, test, and scale.

That means this initial contribution intentionally excludes:

- repeated training variants
- plotting and monitoring helpers
- local outputs and checkpoints
- user-specific absolute paths

## Example

From the repository root:

```bash
uv run python -m aixpert.deepfake_detection.cli summarize \
  --dataset vcapav \
  --data-root /path/to/data \
  --metadata-path /path/to/vcapav_manifest.jsonl \
  --vcapav-split-strategy metadata
```
