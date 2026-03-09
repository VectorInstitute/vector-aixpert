# AIXpert at Vector Institute

[![code checks](https://github.com/VectorInstitute/vector-aixpert/actions/workflows/code_checks.yml/badge.svg)](https://github.com/VectorInstitute/vector-aixpert/actions/workflows/code_checks.yml)
[![unit tests](https://github.com/VectorInstitute/vector-aixpert/actions/workflows/unit_tests.yml/badge.svg)](https://github.com/VectorInstitute/vector-aixpert/actions/workflows/unit_tests.yml)
[![integration tests](https://github.com/VectorInstitute/vector-aixpert/actions/workflows/integration_tests.yml/badge.svg)](https://github.com/VectorInstitute/vector-aixpert/actions/workflows/integration_tests.yml)
[![docs](https://github.com/VectorInstitute/vector-aixpert/actions/workflows/docs.yml/badge.svg)](https://github.com/VectorInstitute/vector-aixpert/actions/workflows/docs.yml)

---

*Codebase and research artifacts developed by the Vector Institute for the AIXpert Horizon Europe project.*

> This repository provides implementations, experiments, and supporting components related to **explainable**, **accountable**, and **trustworthy** AI systems — focusing on agentic AI, multimodal models, and evaluation frameworks.

🔗 **Project website:** [vectorinstitute.github.io/vector-aixpert](https://vectorinstitute.github.io/vector-aixpert/) · **AIXpert consortium:** [aixpert-project.eu](https://aixpert-project.eu/)

---

## About AIXpert

**AIXpert** is a Horizon Europe research initiative focused on building transparent, explainable, and accountable AI systems that can be trusted in real-world applications. The project develops an architecture-agnostic, situation-aware agentic AI platform integrating multi-agent systems, multimodal foundation models, and human feedback to improve transparency and governance of AI systems.

Key challenges addressed:

- **Explainability and interpretability** of AI decisions
- **Transparency and accountability** in AI workflows
- **Bias mitigation** and responsible AI governance
- **Human-AI collaboration** and oversight

AIXpert brings together a consortium of 17 partners across Europe and Canada, combining expertise from academia, industry, and research institutes to build a human-centric AI framework aligned with FATE principles (Fairness, Accountability, Transparency, Ethics).

---

## Repository Structure

```
vector-aixpert/
│
├── src/aixpert/
│   ├── controlled_images/                  # Baseline vs fairness-aware image generation
│   ├── data_generation/
│   │   ├── synthetic_data_generation/
│   │   │   ├── images/                     # Domain/risk-specific image + VQA generation
│   │   │   ├── nlp/                        # Scene descriptions and MCQ generation
│   │   │   └── videos/                     # Video synthesis via Google Veo / Gemini
│   │   └── agent_pipeline/                 # Single-agent CrewAI orchestration
│   ├── toxicity_fairness_analysis/         # Fairness metrics and zero-shot explainability
│   │
│   ├── sonic-o1/                           # [submodule] SONIC-O1 Audio-Video benchmark
│   ├── sonic-o1-agent/                     # [submodule] SONIC-O1 multi-agent framework
│   ├── unified-xai-evaluation-framework/   # [submodule] Explainable agentic evaluation
│   ├── factual-preference-alignment/       # [submodule] F-DPO hallucination reduction
│   ├── bias-in-the-picture-benchmark/      # [submodule] VLM bias benchmarking
│   ├── agentic-transparency/               # [submodule] Agentic AI transparency survey
│   └── humanibench/                        # [submodule] Human-centric fairness benchmark
│
├── notebooks/                              # Research notebooks and experiments
├── scripts/                                # Utilities and experiment scripts
├── docs/                                   # MkDocs documentation sources
├── tests/                                  # Unit and integration tests
└── README.md
```

Each module inside `src/aixpert/` has its own README describing implementation details, dependencies, usage instructions, and references to related papers or project pages.

To clone with all submodules:

```bash
git clone --recurse-submodules https://github.com/VectorInstitute/vector-aixpert
# or if already cloned:
git submodule update --init --recursive
```

---

## Getting Started

Ensure you have [uv](https://docs.astral.sh/uv/getting-started/installation/) installed.

```bash
# 1) Create the environment
uv sync
source .venv/bin/activate

# 2) (Optional) Install dev tools
uv sync --dev

# 3) (Optional) Serve docs locally
uv sync --no-group docs
uv run mkdocs serve
```

### Module quickstarts

- **Controlled Images** — Matched baseline vs fairness-aware images across professions.
  ➜ [`src/aixpert/controlled_images/README.md`](src/aixpert/controlled_images/README.md)

- **Agent Pipeline (CrewAI)** — Single-agent orchestration for prompt/image/metadata generation.
  ➜ [`src/aixpert/data_generation/agent_pipeline/README.md`](src/aixpert/data_generation/agent_pipeline/README.md)

- **Synthetic Data · Images** — Domain/risk-specific image prompts and VQA pairs.
  ➜ [`src/aixpert/data_generation/synthetic_data_generation/images/README.md`](src/aixpert/data_generation/synthetic_data_generation/images/README.md)

- **Synthetic Data · NLP** — Scene descriptions and MCQ generation for text pipelines.
  ➜ [`src/aixpert/data_generation/synthetic_data_generation/nlp/README.md`](src/aixpert/data_generation/synthetic_data_generation/nlp/README.md)

- **Fairness & Explainability** — Statistical Parity, Equal Opportunity, and zero-shot explainers.
  ➜ [`src/aixpert/toxicity_fairness_analysis/README.md`](src/aixpert/toxicity_fairness_analysis/README.md)

For external projects (submodules), see their own READMEs inside `src/aixpert/` or visit the [Projects page](https://vectorinstitute.github.io/vector-aixpert/projects/).

---

## Testing & CI/CD

- Unit and integration tests via `pytest`
- Code quality enforced via `pre-commit` hooks: `ruff`, `mypy`, `typos`, `nbQA`
- Continuous checks through GitHub Actions (see badges above)

---

## Maintainers

**Vector Institute for Artificial Intelligence**

Project Lead: Shaina Raza, PhD

For questions or issues, please open a GitHub issue.

---

## Contributing

We welcome contributions including research prototypes, experimental implementations, evaluation tools, and documentation improvements.

See [CONTRIBUTING.md](CONTRIBUTING.md) for coding standards, dev setup, and workflow conventions. Please open an issue or pull request to discuss potential contributions.

---


## Responsible AI Notice

This repository may generate synthetic data containing demographic attributes for fairness research. These datasets are designed for **controlled bias analysis** and **responsible AI evaluation** only. They are not intended to represent or target real individuals. All data generation follows Vector Institute's responsible AI guidelines and AIXpert's ethical framework.

---

## Funding Acknowledgment

Resources used in preparing this research were provided, in part, by the Province of Ontario, the Government of Canada through CIFAR, and companies sponsoring the Vector Institute.

This work is part of the AIXpert project, funded by the **European Union's Horizon Europe Research and Innovation Programme** under Grant Agreement No. **101214389**, and the **Swiss State Secretariat for Education, Research and Innovation (SERI)**. Views expressed are those of the authors and do not necessarily reflect those of the European Union or funding authorities.

🌐 [Project Website](https://aixpert-project.eu/) · [LinkedIn](https://www.linkedin.com/company/aixpert-project/) · [X/Twitter](https://x.com/AIXPERT_project) · [YouTube](https://www.youtube.com/@AIXPERT_project)