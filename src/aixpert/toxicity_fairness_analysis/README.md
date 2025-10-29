# Toxicity Fairness Analysis with Zero-Shot LLMs and Integrated Gradients

Zero-shot toxicity classification with Integrated Gradients explanations and fairness analysis across demographic identity groups for Responsible AI evaluation.

## Pipeline Overview
- Zero-shot toxicity/hate/offense classification using LLMs
- Integrated Gradients (IG) token attribution explanations
- Token-level attribution heatmap visualization
- Fairness metrics computation across demographic groups
- Dataset downloading utilities for social bias benchmarks

## Features
- Log-probability-based zero-shot classification (no fine-tuning required)
- Integrated Gradients for model interpretability
- Group fairness metrics (SPD, Equal Opportunity, worst-case)
- Multi-dataset support (Jigsaw, CivilComments, SBIC, HateXplain)
- Resume-safe Parquet/CSV I/O
- GPU/CPU automatic device selection

## File Overview
| File | Purpose |
|------|---------|
| `llm_zero_shot_explain.py` | Core zero-shot classification engine with Integrated Gradients explanations. |
| `fairness_metrics.py` | Computes per-group fairness metrics (Accuracy, F1, TPR, FPR, SPD, EOpp). |
| `download_data.py` | Download and normalize social bias datasets from Hugging Face. |
| `sample_jigsaw.py` | Convert Kaggle Jigsaw CSV to normalized Parquet format. |

## Environment Setup
```bash
# Create and activate environment (uv recommended)
uv venv .venv
source .venv/bin/activate

# Install dependencies
uv pip install "transformers>=4.44" accelerate safetensors sentencepiece huggingface-hub
uv pip install datasets tqdm pandas scikit-learn matplotlib numpy
# Parquet support (optional; can use CSV)
uv pip install --only-binary=:all: fastparquet cramjam
```

### Required Environment Variables
No API keys required for core functionality (uses local Hugging Face models).

## Configuration Files
No configuration files required. All parameters passed via command-line arguments.

## Data Formats

### Input Datasets
Supported datasets via `download_data.py`:
- **Jigsaw Unintended Bias**: 26+ identity dimensions (gender, race, religion, sexual orientation)
- **CivilComments**: Toxicity labels with 7 toxicity sub-types
- **CivilComments-WILDS**: Bias benchmarking variant
- **SBIC (Social Bias Frames)**: Post-level bias/offense scores
- **HateXplain**: Hate speech with human rationales

Expected columns:
```json
{
  "comment_text": "Text content to classify",
  "target": 0 or 1,  // binary toxicity label
  "male": 0.0-1.0,   // identity attribute scores
  "female": 0.0-1.0,
  "black": 0.0-1.0,
  // ... additional identity columns
}
```

### Predictions Output (Stage 1)
Saved as: `zs_preds.parquet`
```json
{
  "idx": 0,
  "pred": 0,           // 1 if score > 0, else 0
  "score": -2.34,      // log P(positive) - log P(negative)
  "lp_pos": -5.23,     // log probability of positive label
  "lp_neg": -2.89,     // log probability of negative label
  "target": 1,         // copied label column (if --label_col specified)
  "male": 0.0,         // copied identity columns (if --id_cols specified)
  "female": 1.0,
  // ... additional identity attributes
}
```

### Integrated Gradients Metadata (Stage 1)
Saved as: `zs_preds.ig.parquet`
```json
{
  "idx": 0,
  "heatmap": "outputs/ig_heatmaps/row0.png",
  "prompt": "Full formatted prompt used"
}
```

### Fairness Reports (Stage 2)

**Per-group metrics**: `fairness_report.csv`
```csv
identity,group,n,skipped,acc,f1,tpr,false_positive_rate,pos_rate
male,male=0,500,False,0.85,0.72,0.68,0.12,0.35
male,male=1,500,False,0.82,0.68,0.62,0.15,0.38
```

**Per-identity disparities**: `fairness_report.per_identity.csv`
```csv
identity,SPD,EOpp_diff,n_A0,n_A1
male,0.03,0.06,500,500
female,-0.03,-0.06,500,500
```

**Summary statistics**: `fairness_report.summary.csv`
```csv
WorstAbsSPD,WorstAbsEOpp,WorstGroupAcc,WorstGroupF1
0.15,0.12,0.72,0.58
```

## Running the Pipeline

### Stage 1: Download Dataset
```bash
# Jigsaw Unintended Bias (26+ identity attributes)
uv run python scripts/download_data.py \
  --dataset jigsaw \
  --out data/jigsaw.parquet \
  --sample 50000

# CivilComments (toxicity sub-types)
uv run python scripts/download_data.py \
  --dataset civil \
  --out data/civil.parquet \
  --sample 100000

# CivilComments-WILDS (bias benchmarking)
uv run python scripts/download_data.py \
  --dataset wilds \
  --out data/civil_wilds.parquet \
  --sample 50000

# SBIC (Social Bias Inference Corpus)
uv run python scripts/download_data.py \
  --dataset sbic \
  --out data/sbic.parquet \
  --sample 50000

# HateXplain (hate speech with rationales)
uv run python scripts/download_data.py \
  --dataset hatexplain \
  --out data/hatexplain.parquet \
  --sample 20000
```

**Streaming support** for large datasets:
```bash
# Stream without loading into RAM, limit to 10000 rows
uv run python scripts/download_data.py \
  --dataset civil \
  --out data/civil.parquet \
  --stream \
  --take 10000
```

### Stage 2: Zero-Shot Classification with IG Explanations
```bash
# Quick dry run with small model
uv run python scripts/llm_zero_shot_explain.py \
  --in data/jigsaw.parquet \
  --text_col comment_text \
  --task toxicity \
  --out outputs/zs_preds.parquet \
  --model distilgpt2 \
  --max_rows 1000 \
  --ig_rows 25 \
  --ig_steps 32 \
  --save_heatmaps \
  --force_float32 \
  --label_col target \
  --id_cols male female black white muslim jewish

# Production run with larger model
uv run python scripts/llm_zero_shot_explain.py \
  --in data/jigsaw.parquet \
  --text_col comment_text \
  --task toxicity \
  --out outputs/zs_preds.parquet \
  --model meta-llama/Llama-3.2-1B-Instruct \
  --max_rows 10000 \
  --ig_rows 100 \
  --ig_steps 50 \
  --save_heatmaps \
  --label_col target \
  --id_cols male female black white muslim jewish christian transgender homosexual_gay_or_lesbian
```

**Supported tasks**:
- `toxicity`: Labels = ["toxic", "non-toxic"]
- `hate`: Labels = ["hateful", "not hateful"]
- `offense`: Labels = ["offensive", "not offensive"]

**Key parameters**:
- `--model`: Hugging Face model name (e.g., `distilgpt2`, `meta-llama/Llama-3.2-1B-Instruct`)
- `--max_rows`: Maximum rows to process (default: 2000)
- `--ig_rows`: Number of rows to compute Integrated Gradients for (default: 25)
- `--ig_steps`: Number of interpolation steps for IG (default: 32, higher = more accurate but slower)
- `--save_heatmaps`: Generate PNG heatmaps in `outputs/ig_heatmaps/`
- `--label_col`: Label column to copy to output for fairness analysis
- `--id_cols`: Identity columns to copy to output for fairness analysis
- `--force_float32`: Load model in float32 for stable gradients (recommended for IG)

### Stage 3: Fairness Metrics Computation
```bash
# Compute fairness metrics for Jigsaw dataset
# If labels and identity columns are already in predictions file:
uv run python scripts/fairness_metrics.py \
  --preds outputs/zs_preds.parquet \
  --label_col target \
  --id_cols male female black white muslim jewish christian transgender homosexual_gay_or_lesbian \
  --positive_label 1 \
  --min_group_size 1 \
  --out outputs/fairness_report.csv

# If labels/identities are in a separate file:
uv run python scripts/fairness_metrics.py \
  --preds outputs/zs_preds.parquet \
  --labels_file data/jigsaw.parquet \
  --label_col target \
  --id_cols male female black white muslim jewish christian transgender homosexual_gay_or_lesbian \
  --positive_label 1 \
  --min_group_size 1 \
  --out outputs/fairness_report.csv

# For CivilComments (toxicity sub-types as identities)
uv run python scripts/fairness_metrics.py \
  --preds outputs/zs_preds.parquet \
  --label_col target \
  --id_cols severe_toxicity obscene identity_attack insult threat \
  --min_group_size 1 \
  --out outputs/civil_fairness.csv
```

**Outputs**:
- `fairness_report.csv`: Per-group metrics (Acc, F1, TPR, FPR, Positive Pred Rate)
- `fairness_report.per_identity.csv`: Per-identity disparities (SPD, EOpp)
- `fairness_report.summary.csv`: Worst-case summary statistics

### Stage 4: Visualize Fairness Results
```bash
# View summary statistics
uv run python -c "import pandas as pd; print(pd.read_csv('outputs/fairness_report.summary.csv'))"

# Generate SPD and EOpp bar charts
uv run python - <<'PY'
import pandas as pd, matplotlib.pyplot as plt
pi = pd.read_csv('outputs/fairness_report.per_identity.csv')
for col in ['SPD','EOpp_diff']:
    pi.sort_values(col).plot(x='identity', y=col, kind='bar')
    plt.tight_layout()
    plt.savefig(f'outputs/jigsaw_{col}.png', dpi=200)
    plt.close()
print('Saved -> outputs/jigsaw_SPD.png and outputs/jigsaw_EOpp_diff.png')
PY
```

## Output Directory Structure
```
outputs/
├── zs_preds.parquet                    # Predictions with scores + identity columns
├── zs_preds.ig.parquet                 # IG metadata (prompts, heatmap paths)
├── ig_heatmaps/                        # Token attribution heatmaps
│   ├── row0.png
│   ├── row1.png
│   └── ...
├── fairness_report.csv                 # Per-group metrics
├── fairness_report.per_identity.csv    # Per-identity disparities
├── fairness_report.summary.csv         # Worst-case summaries
├── jigsaw_SPD.png                      # Statistical Parity Difference chart
└── jigsaw_EOpp_diff.png                # Equal Opportunity Difference chart
```

## Algorithms & Methods

### Zero-Shot Classification
- **Method**: Log-probability comparison between label pairs
- **Score**: `score = log P(positive_label) - log P(negative_label)`
- **Prediction**: `pred = 1 if score > 0, else 0`
- **Teacher forcing**: For multi-token labels, computes log-prob via forced decoding

### Integrated Gradients (IG)
- **Purpose**: Attribute model predictions to input tokens
- **Formula**: `IG = (x - x₀) ⊙ ∑(α) ∇f(x₀ + α(x - x₀))`
- **Baseline**: Zero embedding vector
- **Path integration**: Linear interpolation from baseline to input over specified steps
- **Normalization**: Attributions normalized so sum of absolute values equals 1.0
- **Visualization**: Bar plot heatmaps showing token-level attributions

### Fairness Metrics
| Metric | Formula | Interpretation |
|--------|---------|----------------|
| **Accuracy** | (TP+TN) / (TP+TN+FP+FN) | Overall correctness |
| **F1-Score** | 2×(Precision×Recall)/(Precision+Recall) | Harmonic mean of precision/recall |
| **TPR (Recall)** | TP / (TP+FN) | True positive rate |
| **FPR** | FP / (FP+TN) | False positive rate |
| **Positive Pred Rate** | P(Ŷ=1) | Proportion predicted positive |
| **SPD** | P(Ŷ=1\|A=1) - P(Ŷ=1\|A=0) | Statistical parity difference |
| **EOpp** | TPR₁ - TPR₀ | Equal opportunity difference |
| **Worst-Case** | Max \|SPD\|, Max \|EOpp\|, Min Acc/F1 | Worst group performance |

## Troubleshooting
| Issue | Fix |
|-------|-----|
| CUDA out of memory | Use smaller model (distilgpt2) or reduce `--max_rows` / `--ig_rows`. |
| Missing identity columns | Check dataset with: `pd.read_parquet('data/jigsaw.parquet').columns.tolist()` |
| Checkpoint never advances | Ensure write permissions for output directories. |
| Invalid Parquet file | Use CSV fallback: script auto-detects format or specify `--out *.csv`. |
| Heatmaps not generated | Ensure `--save_heatmaps` flag is set and `--ig_rows > 0`. |
| Empty fairness report | Check `--min_group_size` (default=30); lower to 1 for small groups. |

## Extensibility
- **Add new tasks**: Update `LABELS` dict in `llm_zero_shot_explain.py:44-49`
- **New fairness metrics**: Extend `metrics_for_group()` in `fairness_metrics.py:70-87`
- **Custom datasets**: Ensure columns match expected format (text + label + identities)
- **Alternate models**: Pass any Hugging Face CausalLM via `--model`

## Security & Responsible Use
- **Content warning**: These datasets contain hateful, offensive, and toxic language.
- **Demographic inference**: Identity attributes are heuristic; validate before research use.
- **Model bias**: Zero-shot LLM predictions may reflect training biases; use fairness metrics.
- **Computational cost**: Large models (LLaMA, GPT) require GPU VRAM; start with distilgpt2.

## Example Workflow: Complete Pipeline

```bash
# 1. Download Jigsaw dataset
uv run python scripts/download_data.py \
  --dataset jigsaw --out data/jigsaw.parquet --sample 50000

# 2. Run zero-shot scoring with IG explanations
uv run python scripts/llm_zero_shot_explain.py \
  --in data/jigsaw.parquet \
  --text_col comment_text \
  --task toxicity \
  --out outputs/zs_preds.parquet \
  --model distilgpt2 \
  --max_rows 1000 \
  --ig_rows 25 --ig_steps 32 --save_heatmaps \
  --force_float32 \
  --label_col target \
  --id_cols male female black white muslim jewish

# 3. Compute fairness metrics
uv run python scripts/fairness_metrics.py \
  --preds outputs/zs_preds.parquet \
  --label_col target \
  --id_cols male female black white muslim jewish \
  --min_group_size 1 \
  --out outputs/fairness_report.csv

# 4. View results
uv run python -c "import pandas as pd; print(pd.read_csv('outputs/fairness_report.summary.csv'))"

# 5. Visualize disparities
uv run python - <<'PY'
import pandas as pd, matplotlib.pyplot as plt
pi = pd.read_csv('outputs/fairness_report.per_identity.csv')
pi.sort_values('SPD').plot(x='identity', y='SPD', kind='bar')
plt.tight_layout()
plt.savefig('outputs/SPD_chart.png', dpi=200)
print('Saved -> outputs/SPD_chart.png')
PY
```

## Dependencies
Core packages:
```
transformers>=4.44
accelerate
safetensors
sentencepiece
huggingface-hub
datasets
tqdm
pandas
scikit-learn
matplotlib
numpy
fastparquet (optional, for Parquet support)
cramjam (optional, for compression)
```

## License
This project is licensed under the MIT License.

## Citation
<!-- TODO -->
