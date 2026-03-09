# Projects

This page summarizes each project's scope and links to its repository, documentation, and quickstart. Installation instructions are in each project's own README.

---

## Overview

- **What is this?** — A collection of research tools, benchmarks, and evaluation frameworks for responsible AI: fairness, explainability, multimodal understanding, and agentic systems.
- **Who is it for?** — Researchers and practitioners working on fairness-aware AI, multimodal benchmarking, explainable agentic systems, and reproducible AI evaluation.
- **How is it organized?** — Some projects have their own standalone repositories; others live as modules in the main [AIXpert repo](https://github.com/VectorInstitute/vector-aixpert). Each section below links to the relevant repo and docs.

---

## SONIC-O1

Real-world benchmark for evaluating multimodal LLMs on **audio-video understanding**: short to long-form videos across 13 conversational domains (job interviews, medical, legal, etc.), with three tasks — summarization, multiple-choice QA, and temporal localization — and demographic metadata for fairness analysis.

**Links:** [GitHub](https://github.com/VectorInstitute/sonic-o1) · [Project page](https://vectorinstitute.github.io/sonic-o1/) · [Dataset](https://huggingface.co/datasets/vector-institute/sonic-o1) · [Leaderboard](https://huggingface.co/spaces/vector-institute/sonic-o1-leaderboard)

---

## SONIC-O1 Multi-Agent

Compound multi-agent system for **audio-video understanding** with Qwen3-Omni: planner, reasoner, and reflection agents with chain-of-thought reasoning, self-reflection, temporal grounding, and optional multi-step task decomposition. Built on LangGraph and vLLM.

**Links:** [GitHub](https://github.com/VectorInstitute/sonic-o1-agent)

---

## Explainable Agentic Evaluation Framework

Framework for evaluating **explainability** in both traditional (static) and **agentic** AI systems. Compares attribution-based explanations (e.g. SHAP, LIME) with trace-based diagnostics; shows that attribution is stable for static prediction but trace-grounded rubrics are needed to localize agentic failures.

**Links:** [GitHub](https://github.com/VectorInstitute/unified-xai-evaluation-framework) · [Project page](https://vectorinstitute.github.io/unified-xai-evaluation-framework/)

---

## Factual Preference Alignment (F-DPO)

Factuality-aware Direct Preference Optimization: extends DPO with binary factuality labels and a factuality-aware margin to reduce LLM hallucinations without an auxiliary reward model. Single-stage and compute-efficient.

**Links:** [GitHub](https://github.com/VectorInstitute/Factual-Preference-Alignment) · [Project page](https://vectorinstitute.github.io/Factual-Preference-Alignment/) · [Dataset](https://huggingface.co/datasets/vector-institute/Factuality_Alignment)

---

## Modules in AIXpert

These modules live in the main [AIXpert](https://github.com/VectorInstitute/vector-aixpert) repository. Clone once, run `uv sync`, then follow the READMEs below for setup and commands.

### Controlled Images

Baseline vs. fairness-aware image sets for occupations or social groups; configurable attributes, matched prompts, and reproducible seeds.

**Links:** [Module README](https://github.com/VectorInstitute/vector-aixpert/blob/main/src/aixpert/controlled_images/README.md)

### Synthetic Data Generation

Multi-modal synthesis: image + VQA pairs, textual scenes and MCQs, and video generation (Veo/Gemini). Driven by LLM-designed prompts and metadata templates.

**Links:** [Images README](https://github.com/VectorInstitute/vector-aixpert/blob/main/src/aixpert/data_generation/synthetic_data_generation/images/README.md) · [NLP README](https://github.com/VectorInstitute/vector-aixpert/blob/main/src/aixpert/data_generation/synthetic_data_generation/nlp/README.md)

### Agent Pipeline (CrewAI)

Single-agent orchestration for prompt → image → metadata generation and large-scale data creation with structured JSON task definitions.

**Links:** [Module README](https://github.com/VectorInstitute/vector-aixpert/blob/main/src/aixpert/data_generation/agent_pipeline/README.md)

### Fairness & Explainability

Statistical metrics (e.g. Statistical Parity, Equal Opportunity), zero-shot explainers (integrated gradients, concept attributions), and visualization (disparity plots, attribution maps).

**Links:** [AIXpert repo](https://github.com/VectorInstitute/vector-aixpert)

---

## Contributing & Documentation

- See [CONTRIBUTING.md](https://github.com/VectorInstitute/vector-aixpert/blob/main/CONTRIBUTING.md) for coding standards (PEP8, Google docstrings), pre-commit hooks (`ruff`, `mypy`, `typos`, `nbQA`), branching, and tests.
- **Run docs locally:** `uv sync --no-group docs` then `mkdocs serve` → [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **CI:** GitHub Actions (`code_checks.yml`, `unit_tests.yml`, `integration_tests.yml`)