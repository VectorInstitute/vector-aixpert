# User Guide

Transparent tools and standardized benchmarks for **fair**, **explainable**, and **accountable** generative AI. This guide introduces modules, setup, and usage patterns for fairness-aware data generation and analysis.

---

## Table of Contents

- [Getting Started](#getting-started)
- [Core Concepts](#core-concepts)
- [Contributing and Documentation](#contributing-and-documentation)

---

## Getting Started

**Four Essential Questions**

| Question | Answer |
|-----------|---------|
| **What is the project about?** | A research framework and toolkit for generating, evaluating, and mitigating bias in multimodal AI systems. |
| **Why Fairness-Aware Synthetic Data?** | Controlled datasets isolate bias-inducing factors, allowing targeted experiments on fairness, explainability, and representation. |
| **Why Agentic AI?** | We use autonomous LLM agents (via **CrewAI**) to scale prompt, image, and metadata generation. |
| **Who is project for?** | Researchers, data scientists, and fairness practitioners studying or benchmarking bias in generative models. |

---

### Installation

#### From source (recommended)

```bash
git clone https://github.com/VectorInstitute/vector-aixpert.git
cd vector-aixpert
uv sync
```

#### Optional groups

```bash
# Development extras
uv sync --dev
# Documentation build
uv sync --no-group docs
```

#### Verify installation

```bash
pytest -q
mkdocs serve
```

---

### Quick Starts

Minimal commands to explore modules.

```bash
# 1. Set up environment
uv sync
source .venv/bin/activate

# 2. Run controlled image generation
cd src/aixpert/controlled_images/
uv run python src/main.py \
  --config configs/img_gen_config.yaml

# 3. Generate synthetic data (text)
cd src/aixpert/data_generation/synthetic_data_generation/nlp/
uv run main.py \
  --config config.yaml \
  --stage all

# 4. Generate synthetic data (images)
cd src/aixpert/data_generation/synthetic_data_generation/images/
uv run main.py all_stages \
  --config_file ../../config.yaml \
  --prompt_yaml prompt_paths.yaml \
  --domain hiring \
  --risk security_risks

# 5. Compute fairness metrics
cd src/aixpert/toxicity_fairness_analysis/

uv run python scripts/download_data.py \
  --dataset jigsaw \
  --out data/jigsaw.parquet \
  --sample 50000

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
  --label_col target
  --id_cols male female black white muslim jewish
```

Each module provides a focused README with configuration details and output examples.

---

### Standard Usage

Typical workflow for fairness-aware data generation:

1. **Generate controlled data**
   Create matched datasets (e.g., gender, occupation, or ethnicity pairs).
2. **Run agentic generation pipeline**
   Use CrewAI agents for multimodal prompt, image, and metadata generation.
3. **Perform fairness analysis**
   Compute bias metrics such as Statistical Parity or Equal Opportunity.
4. **Visualize or export results**
   Generate structured outputs or Hugging Face datasets for benchmarking.

---

## Core Concepts

### Controlled Images

Generates baseline vs fairness-aware image sets for occupations or social groups.
Supports configurable attributes, matched prompts, and consistent random seeds for reproducibility.

### Synthetic Data Generation

Multi-modal data synthesis modules under:

* `synthetic_data_generation/images` — image + VQA pairs
* `synthetic_data_generation/nlp` — textual scenes and MCQs
* `synthetic_data_generation/videos` — Veo/Gemini video generation

Each generator is driven by LLM-designed prompts and metadata templates.

### Agent Pipeline (CrewAI)

Implements single-agent orchestration to chain prompt → image → metadata generation.
Enables autonomous large-scale data creation using structured JSON task definitions.


### Fairness & Explainability

Evaluates generated data and model outputs via:

* **Statistical metrics** — Statistical Parity, Equal Opportunity
* **Zero-shot explainers** — integrated gradients, concept attributions
* **Visualization tools** — disparity plots, attribution maps

### Module Quick Start (one-liners + deep links)

Each core module has its own README with commands, configurations, and sample outputs.

* **Controlled Images** — Generate matched baseline vs fairness-aware images across professions.
  ➜ [`View Module README`](https://github.com/VectorInstitute/vector-aixpert/blob/main/src/aixpert/controlled_images/README.md)

* **Agent Pipeline (CrewAI)** — Single-agent orchestration for prompt, image, and metadata generation.
  ➜ [`View Module README`](https://github.com/VectorInstitute/vector-aixpert/blob/main/src/aixpert/data_generation/agent_pipeline/README.md)

* **Synthetic Data · Images** — Domain- and risk-specific image prompts and VQA pairs.
  ➜ [`View Module README`](https://github.com/VectorInstitute/vector-aixpert/blob/main/src/aixpert/data_generation/synthetic_data_generation/images/README.md)

* **Synthetic Data · NLP** — Scene descriptions and MCQ generation for text pipelines.
  ➜ [`View Module README`](https://github.com/VectorInstitute/vector-aixpert/blob/main/src/aixpert/data_generation/synthetic_data_generation/nlp/README.md)


---

## Contributing and Documentation

See [CONTRIBUTING.md](https://github.com/VectorInstitute/vector-aixpert/blob/main/CONTRIBUTING.md) for:

* Coding standards and style guide (PEP8 + Google docstrings)
* Pre-commit setup (`ruff`, `mypy`, `typos`, `nbQA`)
* Branching and PR workflow
* Test coverage requirements

### Docs build

```bash
uv sync --no-group docs
mkdocs serve
```

The site will be live at [http://127.0.0.1:8000](http://127.0.0.1:8000).

### Testing and Standards

```bash
pytest -v
pre-commit run --all-files
```

Continuous integration runs these via GitHub Actions (`code_checks.yml`, `unit_tests.yml`, `integration_tests.yml`).

---
