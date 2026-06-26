# Vector AIXpert: Responsible AI Infrastructure for Fairness, Explainability, and Evaluation


_**[Vector Institute's](https://vectorinstitute.ai)** contribution to the [AIXpert Project](https://aixpert-project.eu/): tools, benchmarks, and research for **explainable**, **accountable**, and **fair** AI._

> This project represents the Vector Institute's research contributions to the AIXpert Horizon Europe initiative. It focuses on developing tools, datasets, and evaluation pipelines for fairness-aware generative AI and explainable AI systems.

---

## What we do

Vector's contribution to AIXpert spans four core areas:

- **Explainable & accountable AI** — Tools and benchmarks for interpretability, fairness, and transparency in generative and multimodal AI.
- **Trustworthy agentic AI** — Transparent, auditable, human-in-the-loop agentic systems with measurable trustworthiness metrics.
- **Multimodal evaluation** — Benchmarks and datasets for audio-video understanding, vision-language assessment, and fairness across domains and demographics.
- **Open, reproducible research** — Code, datasets, and documentation shared openly to support governance-ready research.

For the full AIXpert vision, consortium, and funding details, see [About](about.md).

---

## System Architecture

Vector's responsible AI pipeline moves data through five stages — from raw inputs to governed, explainable outputs.

??? note "View pipeline"
    <div class="arch-pipeline">
      <div class="arch-step">
        <span class="arch-label">Synthetic Data Generation</span>
        <span class="arch-desc">Fairness-aware multimodal data: images, VQA pairs, text scenes, and video — with demographic metadata and reproducible seeds.</span>
      </div>
      <div class="arch-arrow">↓</div>
      <div class="arch-step">
        <span class="arch-label">Multimodal Pipelines</span>
        <span class="arch-desc">Parallel text, vision, video, and audio agents with attribution hooks and Risk-VQA for bias and toxicity detection.</span>
      </div>
      <div class="arch-arrow">↓</div>
      <div class="arch-step">
        <span class="arch-label">Agentic AI Evaluation</span>
        <span class="arch-desc">Traceable planning and execution agents with RAG/memory, tool registry, and sandboxed task execution.</span>
      </div>
      <div class="arch-arrow">↓</div>
      <div class="arch-step">
        <span class="arch-label">Fairness Metrics + Explainability</span>
        <span class="arch-desc">Statistical parity, equal opportunity, attribution and trace-based diagnostics — with disparity plots and explanation bundles.</span>
      </div>
      <div class="arch-arrow">↓</div>
      <div class="arch-step arch-step--last">
        <span class="arch-label">Responsible AI Insights</span>
        <span class="arch-desc">Human-in-the-loop review, signed Governance Log (prompts, tool calls, safety decisions), and final explainable outputs.</span>
      </div>
    </div>

---

## Recent Updates

- :material-scale-balance: **UnBias-Plus** — Bias detection and debiasing toolkit — paper, CLI, REST API, Python, and live demo. [Project page](https://vectorinstitute.github.io/unbias-plus/) · [Code](https://github.com/VectorInstitute/unbias-plus) · [Demo](https://unbias-plus.vectorinstitute.ai/). [More on Updates](updates.md).
- :material-account-group: **AI4Good Lab 2026** — Shaina Raza, PhD and Ahmed Y. Radwan presented **UnBias-Plus** and disinformation detection research at the [AI4Good Lab](https://www.ai4goodlab.com/) 2026 Toronto cohort. [More on Updates](updates.md).
- :material-presentation: **Toronto Machine Learning Summit** — Ahmed Y. Radwan presented **SONIC-O1** at the [Toronto Machine Learning Summit](https://www.torontomachinelearning.com/) (16–19 June 2026). [Project page](https://vectorinstitute.github.io/sonic-o1/) · [Code](https://github.com/VectorInstitute/sonic-o1) · [Leaderboard](https://huggingface.co/spaces/vector-institute/sonic-o1-leaderboard). [More on Updates](updates.md).
- :material-handshake: **HAICON26 & Vector–Helmholtz Munich MOU** — Shaina Raza, PhD presented at [HAICON 2026](https://haicon.cc/) (8–11 June 2026, Munich) and Vector Institute signed an MOU with Helmholtz Munich's Computational Health Center. [More on Updates](updates.md).
- :material-map-marker: **AIXpert General Assembly — Barcelona 2026** — The AIXPERT consortium met at the Barcelona Supercomputing Center (3–4 June 2026) to align the technical roadmap for year two. [More on Updates](updates.md).
- :material-trophy: **The Peak Emerging Leaders 2026** — Shaina Raza, PhD recognized in [The Peak's Emerging Leaders 2026](https://emergingleaders.readthepeak.com/2026/artificial-intelligence) in the Artificial Intelligence category. [More on Updates](updates.md).
- :material-leaf: **ICML 2026** — [_Position: Sustainable Open-Source AI Requires Tracking the Cumulative Footprint of Derivatives_](https://arxiv.org/abs/2601.21632). [Project page](https://vectorinstitute.github.io/ai-impact-accounting/). [More on Updates](updates.md).
- :material-chart-bar: **AgentFinVQA** — Auditable multi-agent pipeline for financial chart QA with traceable Model Evaluation Packets. [Project page](https://vectorinstitute.github.io/AgentFinVQA/) · [Code](https://github.com/VectorInstitute/AgentFinVQA/). [More on Updates](updates.md).
- :material-shield-search: **FairSense-AgentiX** — Agentic fairness and AI-risk analysis for text, images, and datasets. [Project page](https://vectorinstitute.github.io/fairsense-agentix/) · [Code](https://github.com/VectorInstitute/fairsense-agentix). [More on Updates](updates.md).
- :material-check-decagram: **Evaluating and Regulating Agentic AI** — Published in *Information Fusion*, Elsevier 2026. [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S1566253526003246) · [Code](https://github.com/itsazibfarooq/agenticEvaluation). [More on Updates](updates.md).
- :material-check-decagram: **Model immunization** — Accepted at WCCI 2026 (IJCNN). [arXiv](https://arxiv.org/abs/2505.17870) · [Project page](https://shainarazavi.github.io/ai-vaccine/) · [Code](https://github.com/shainarazavi/ai-vaccine). [More on Updates](updates.md).
- :material-check-decagram: **F-DPO** — ACL 2026 Findings. [arXiv](https://arxiv.org/abs/2601.03027) · [Project page](https://vectorinstitute.github.io/Factual-Preference-Alignment/) · [Code](https://github.com/VectorInstitute/Factual-Preference-Alignment). [More on Updates](updates.md).
- :material-check-decagram: **TRiSM for Agentic AI** — Published at [AI Open, Elsevier 2026](https://doi.org/10.1016/j.aiopen.2026.02.006). [More on Updates](updates.md).
- :material-robot: **SONIC-O1 Multi-Agent** — Multi-agent framework for audio-video understanding with Qwen3-Omni. [Code](https://github.com/VectorInstitute/sonic-o1-agent). [More on Updates](updates.md).
- :material-play-circle: **SONIC-O1** — Paper: [_A Real-World Benchmark for Evaluating MLLMs on Audio-Video Understanding_](https://arxiv.org/abs/2601.21666). [Dataset](https://huggingface.co/datasets/vector-institute/sonic-o1) · [Leaderboard](https://huggingface.co/spaces/vector-institute/sonic-o1-leaderboard). [More on Updates](updates.md).

[:material-arrow-right: **View full list**](updates.md){ .md-button .md-button--primary }

---

## Related Projects

A snapshot of Vector's key contributions within AIXpert. Each project has its own repository, documentation, and quickstart.

<div class="grid cards" markdown>

-   :material-scale-balance: **UnBias-Plus**

    AI-driven toolkit for bias detection and debiasing in text: biased spans, severity, reasoning, neutral replacements, and a full neutral rewrite for more trustworthy workflows.

    [:material-arrow-right: Project page](https://vectorinstitute.github.io/unbias-plus/) · [Code](https://github.com/VectorInstitute/unbias-plus) · [PyPI](https://pypi.org/project/unbias-plus/)

-   :material-shield-search: **FairSense-AgentiX**

    Agentic workflows for bias detection and risk assessment on text, images, and datasets—planning, tool use, self-critique, and telemetry-backed explanations.

    [:material-arrow-right: Project page](https://vectorinstitute.github.io/fairsense-agentix/) · [Code](https://github.com/VectorInstitute/fairsense-agentix) · [PyPI](https://pypi.org/project/fairsense-agentix/)

-   :material-chart-bar: **SONIC-O1**

    Real-world benchmark for evaluating MLLMs on audio-video understanding, with a public leaderboard.

    [:material-arrow-right: Dataset](https://huggingface.co/datasets/vector-institute/sonic-o1) · [Code](https://github.com/VectorInstitute/sonic-o1) · [Leaderboard](https://huggingface.co/spaces/vector-institute/sonic-o1-leaderboard)

-   :material-robot: **SONIC-O1 Multi-Agent**

    Multi-agent framework for audio-video understanding with chain-of-thought reasoning, self-reflection, and temporal grounding.

    [:material-arrow-right: Code](https://github.com/VectorInstitute/sonic-o1-agent)

-   :material-magnify: **Explainable Agentic Evaluation Framework**

    Analyzes reasoning traces and interpretability of agentic AI across static and agentic settings.

    [:material-arrow-right: Code](https://github.com/VectorInstitute/unified-xai-evaluation-framework) · [Project page](https://vectorinstitute.github.io/unified-xai-evaluation-framework/)

-   :material-tune: **Factual Preference Alignment (F-DPO)**

    Factuality-aware preference learning to reduce LLM hallucinations without a separate reward model.

    [:material-arrow-right: Paper](https://arxiv.org/abs/2601.03027) · [Project page](https://vectorinstitute.github.io/Factual-Preference-Alignment/) · [Code](https://github.com/VectorInstitute/Factual-Preference-Alignment)

-   :material-image-multiple: **HumaniBench**

    Fairness-focused vision-language benchmark evaluating foundation models across human-centric demographics.

    [:material-arrow-right: Project page](https://vectorinstitute.github.io/HumaniBench/)

-   :material-shield-check: **Agentic Transparency**

    Survey and framework on interpretability, explainability, and governance of agentic AI systems.

    [:material-arrow-right: Project page](https://vectorinstitute.github.io/Agentic-Transparency/)

</div>

[:material-arrow-right: **View all papers**](papers.md){ .md-button .md-button--primary }
[:material-book-open-variant: **Projects & quickstarts**](projects.md){ .md-button }

---

## Citation

If you use any of our tools, datasets, or benchmarks, please cite the relevant work. BibTeX entries are available on each paper's entry in the [Papers](papers.md) page.

---

!!! warning "Responsible AI Notice"
    This project may generate synthetic data containing demographic attributes for fairness research.
    These datasets are designed for **controlled bias analysis** and **responsible AI evaluation** only.
    They are not intended to represent or target real individuals.
    All data generation follows Vector Institute's responsible AI guidelines and AIXpert's ethical framework.

---

> Have feedback or want to contribute? See the [:material-account-group: Team](about.md#team) section on About and open an issue or pull request.
