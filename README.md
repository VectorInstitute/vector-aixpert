# 🧠 AI Fairness Data Generation and Question Answering System

[![code checks](https://github.com/VectorInstitute/vector-aixpert/actions/workflows/code_checks.yml/badge.svg)](https://github.com/VectorInstitute/vector-aixpert/actions/workflows/code_checks.yml)
[![unit tests](https://github.com/VectorInstitute/vector-aixpert/actions/workflows/unit_tests.yml/badge.svg)](https://github.com/VectorInstitute/vector-aixpert/actions/workflows/unit_tests.yml)
[![integration tests](https://github.com/VectorInstitute/vector-aixpert/actions/workflows/integration_tests.yml/badge.svg)](https://github.com/VectorInstitute/vector-aixpert/actions/workflows/integration_tests.yml)
[![docs](https://github.com/VectorInstitute/vector-aixpert/actions/workflows/docs.yml/badge.svg)](https://github.com/VectorInstitute/vector-aixpert/actions/workflows/docs.yml)

<!--
[![codecov](https://codecov.io/github/VectorInstitute/vector-aixpert/graph/badge.svg?token=83MYFZ3UPA)](https://codecov.io/github/VectorInstitute/vector-aixpert)
![GitHub License](https://img.shields.io/github/license/VectorInstitute/vector-aixpert)
-->

---

*Transparent tools and standardized benchmarks for **fair**, **explainable**, and **accountable** generative AI.*

> The rapid expansion of GenAI magnifies long-standing concerns around **bias, fairness, and representation**.
> This project enables systematic, controlled experimentation so researchers can identify *when* and *why* bias occurs, and test what mitigates it.

---

## 🌍 What is the project about?

The **AI Fairness Data Generation and Question Answering System** is part of **[Vector Institute's](https://vectorinstitute.ai)** contribution to the broader [AIXPERT Project](https://aixpert-project.eu/), a multi-institutional initiative, to develop tools and benchmarks for **fairness-aware data generation and evaluation** in generative AI.

It provides:

* 🧩 **Controlled synthetic datasets** — safely isolate bias-inducing factors.
* 🤖 **Agentic automation** using **CrewAI** and custom LLM agents.
* 📊 **Fairness metrics & explainers** to visualize disparities.
* ⚙️ **Configurable, reproducible pipelines** for responsible AI research.

📘 **Documentation:** [Project website](https://vectorinstitute.github.io/vector-aixpert/)

📂 **Data:** [Hugging Face](https://huggingface.co/datasets/vector-institute/aixpert)

🧮 **Code:** [GitHub Page](https://github.com/VectorInstitute/vector-aixpert)

---

## 🧱 Repository Structure

| Path                                                            | Description                                                           |
| --------------------------------------------------------------- | --------------------------------------------------------------------- |
| `src/aixpert/controlled_images/`                                | Controlled image generation (baseline vs fairness-aware).             |
| `src/aixpert/data_generation/synthetic_data_generation/images/` | Domain- and risk-specific image + VQA generation.                     |
| `src/aixpert/data_generation/synthetic_data_generation/nlp/`    | Domain- and risk-specific Scene + MCQ generation.                                      |
| `src/aixpert/data_generation/synthetic_data_generation/videos/` | Video synthesis using Google Veo / Gemini API.                        |
| `src/aixpert/data_generation/agent_pipeline/`                   | Single-agent **CrewAI** pipeline for multimodal orchestration.        |
| `src/aixpert/toxicity_fairness_analysis/`                                    | Fairness metrics and zero-shot explainability (integrated gradients). |
| `docs/`                                                         | MkDocs documentation sources.                                         |
| `tests/`                                                        | Tests using `pytest`.                            |

---

## 🚀 Getting Started

New to the project? Follow the steps below to set up your development environment and explore key modules.

### Prerequisites

Ensure you have [uv](https://docs.astral.sh/uv/getting-started/installation/) installed (recommended environment manager).

### Quick setup
```bash
# 1) Create the environment
uv sync
source .venv/bin/activate

# 2) (Optional) Install dev tools
uv sync --dev

# 3) (Optional) Install and Serve docs
uv sync --no-group docs
uv run mkdocs serve
````

### Module quick start (one-liners + deep links)

Each module below has its own README with exact commands, configs, and outputs.

* **Controlled Images** — Generate matched baseline vs fairness-aware images across professions.
  ➜ [`src/aixpert/controlled_images/README.md`](src/aixpert/controlled_images/README.md)

* **Agent Pipeline (CrewAI)** — Single-agent orchestration for prompt/image/metadata generation.
  ➜ [`src/aixpert/data_generation/agent_pipeline/README.md`](src/aixpert/data_generation/agent_pipeline/README.md)

* **Synthetic Data · Images** — Domain/risk-specific image prompts and VQA pairs.
  ➜ [`src/aixpert/data_generation/synthetic_data_generation/images/README.md`](src/aixpert/data_generation/synthetic_data_generation/images/README.md)

* **Synthetic Data · NLP** — Scene descriptions and MCQ generation for text pipelines.
  ➜ [`src/aixpert/data_generation/synthetic_data_generation/nlp/README.md`](src/aixpert/data_generation/synthetic_data_generation/nlp/README.md)

<!--
# TODO: Add the video module readme when ready
# * **Synthetic Data · Videos** — Video synthesis via Google Veo / Gemini with checkpoint & resume.
  # ➜ [`src/aixpert/data_generation/synthetic_data_generation/videos/README.md`](src/aixpert/data_generation/synthetic_data_generation/videos/README.md)
-->

* **Fairness & Explainability (Toxicity fairness analysis)** — Metrics (Statistical Parity, Equal Opportunity) + zero-shot explainers (integrated gradients).
  ➜ [`src/aixpert/toxicity_fairness_analysis/README.md`](src/aixpert/toxicity_fairness_analysis/README.md)

* **Documentation** — MkDocs site sources; how to extend and publish docs.
  ➜ [`CONTRIBUTING.md`](CONTRIBUTING.md)

<!--
* **Tests** — Run unit/integration tests with `pytest` and pre-commit hooks.
  ➜ [`tests/README.md`](tests/README.md)
-->

<!-- # TODO: Add the website link when the docs are published on GitHub Pages
# > Prefer a website? See the full docs:
# > 🔗 **AIXpert website** — [https://vectorinstitute.github.io/AIXpert/](https://vectorinstitute.github.io/vector-aixpert/)
 -->

---

## 🧠 Key Components

* **🎨 Controlled Image Generation:** Produces matched baseline vs fairness-aware images across professions.
* **🤖 Agentic AI (CrewAI):** LLM-based prompt, image, and metadata orchestration.
* **🧾 Synthetic Data Generation:** Domain/risk-specific image prompts, VQA pairs, scenes, and MCQs.
* **🎬 Video Generation:** Uses Google Veo/Gemini APIs with checkpoint and resume logic.
* **⚖️ Fairness Metrics & Explainability:** Statistical Parity, Equal Opportunity, and zero-shot explainers with integrated gradients.

---

## 🧪 Testing & CI/CD

* Unit and integration tests via `pytest`.
* Code quality enforced via `pre-commit` hooks:

  * `ruff` — linting & formatting
  * `mypy` — type checks
  * `typos` — spell checks
  * `nbQA` — notebook linting
* Continuous checks through GitHub Actions (see badges above).

---

## 📚 Publications & Outputs

* 🧩 [*Bias in the Picture: Benchmarking VLMs with Social-Cue News Images*](https://arxiv.org/abs/2509.19659), NeurIPS LLM Evals Workshop 2025
* 📜 [*TRiSM for Agentic AI*](https://arxiv.org/abs/2506.04133), Preprint
* 📘 [*Responsible Agentic Reasoning and AI Agents*](https://www.techrxiv.org/articles/1329333), TechRxiv
* 🧠 *Single-Agent TRiSM Poster (NeurIPS LAW Workshop 2025)*

---

## 🤝 Contributing

We welcome community contributions!
See [CONTRIBUTING.md](CONTRIBUTING.md) for coding standards, dev setup, and workflow conventions.


---

## 📄 License

This code in this repo is released under the **MIT License**.

---

## 💡 About AIXPERT

The **AIXPERT Project** unites 17 partners across Europe and Canada under the
**EU Horizon Europe Programme (Grant No. 101214389)** and the **Swiss SERI** to advance
**explainable, fair, and accountable AI**.

🌐 [Project Website](https://aixpert-project.eu/) · [LinkedIn](https://www.linkedin.com/company/aixpert-project/) · [X/Twitter](https://x.com/AIXPERT_project) · [YouTube](https://www.youtube.com/@AIXPERT_project)

---

## 💰 Funding Acknowledgment

> The **AIXPERT Project** has received funding from the **European Union’s Horizon Europe Research and Innovation Programme** under Grant No. **101214389**, and from the **Swiss State Secretariat for Education, Research and Innovation (SERI)**.
> Views expressed are those of the authors and do not necessarily reflect those of the European Union or funding authorities.
