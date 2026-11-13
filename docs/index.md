# Vector AIXpert: Responsible AI Infrastructure for Fairness, Explainability, and Evaluation


_**[Vector Institute's](https://vectorinstitute.ai)** contribution to the [AIXpert Project](https://aixpert-project.eu/): tools, benchmarks, and research for **explainable**, **accountable**, and **fair** AI._

> This project represents the Vector Institute's research contributions to the AIXpert Horizon Europe initiative. It focuses on developing tools, datasets, and evaluation pipelines for fairness-aware generative AI and explainable AI systems.

---

## What we do

Vector's contribution to AIXpert spans four core areas:

- **Explainable & accountable AI**. Tools and benchmarks for interpretability, fairness, and transparency in generative and multimodal AI.
- **Trustworthy agentic AI**. Transparent, auditable, human-in-the-loop agentic systems with measurable trustworthiness metrics.
- **Multimodal evaluation**. Benchmarks and datasets for audio-video understanding, vision-language assessment, and fairness across domains and demographics.
- **Open, reproducible research**. Code, datasets, and documentation shared openly to support governance-ready research.

For the full AIXpert vision, consortium, and funding details, see [About](about.md).

---

## System Architecture

Vector's responsible AI pipeline moves data through five stages: from raw inputs to governed, explainable outputs.

<div class="arch-pipeline">
  <div class="arch-step">
    <span class="arch-label">Synthetic Data Generation</span>
    <span class="arch-desc">Fairness-aware multimodal data: images, VQA pairs, text scenes, and video, with demographic metadata and reproducible seeds.</span>
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
    <span class="arch-desc">Statistical parity, equal opportunity, attribution and trace-based diagnostics, with disparity plots and explanation bundles.</span>
  </div>
  <div class="arch-arrow">↓</div>
  <div class="arch-step arch-step--last">
    <span class="arch-label">Responsible AI Insights</span>
    <span class="arch-desc">Human-in-the-loop review, signed Governance Log (prompts, tool calls, safety decisions), and final explainable outputs.</span>
  </div>
</div>

---

## Recent Updates

- :material-rocket-launch: **MARS**. Video forgery detector for facial manipulation and fully generated video that reports the frames and regions it used. [Project page](https://vectorinstitute.github.io/mars/) · [Preprint](https://arxiv.org/abs/2611.12508) · [Code](https://github.com/VectorInstitute/mars).
- :material-database: **Mozaic**. Audio-video deepfake benchmark that labels the face and the voice separately and asks which part is fake, what kind, whose identity, and why. Zero-shot models catch fake video far more often than fake audio. Paper coming. [Project page](https://vectorinstitute.github.io/mozaic/) · [Code](https://github.com/VectorInstitute/mozaic) · [Dataset](https://huggingface.co/datasets/vector-institute/Mozaic).
- :material-newspaper: **Deepfakes in The New York Times**. Coverage of AI-generated fakes in midterm memes (12 Nov 2026). [Article](https://www.nytimes.com/2026/11/12/technology/artifical-intelligence-fakes-midterm-memes.html).
- :material-presentation: **CIFAR AI Safety Week**. Shaina Raza presented deepfake generation and detection, including **MARS** and **Mozaic**, at CAISI during CIFAR AI Safety Week (12 Nov 2026, Toronto). [Post](https://www.linkedin.com/posts/cifar_as-ai-safety-week-wraps-up-in-toronto-researchers-activity-7527029349343068161-garv).
- :material-presentation: **NVIDIA: Responsible AI & Transparency**. Shaina Raza presented **DIA** as a lightweight transparency layer for the energy, water, and carbon footprint of open models and their derivatives (1:30–1:50 pm). [Project](https://vectorinstitute.github.io/ai-impact-accounting/).
- :material-presentation: **MLOps North 2026**. Shaina Raza spoke on responsible AI beyond accuracy: fairness, safety, and sustainability, from agent trajectories to safety, reliability, and governance (5–6 Nov 2026, Toronto). [Summit](https://www.torontomachinelearning.com/) · [Presenter page](https://www.torontomachinelearning.com/presenter/shaina-raza/).
- :material-newspaper: **Deepfakes in the Niagara Falls Review**. A Toronto expert on red flags in deepfake videos. [Article](https://www.niagarafallsreview.ca/news/municipal-elections/deepfake-videos-online-toronto-expert-explains-red-flags/article_408c9887-c76a-5c62-a55a-39460cb59d71.html).
- :material-check-decagram: **FairSense-AgentiX published in JOSS**. Agentic fairness and AI-risk platform for text, images, and datasets. [Paper](https://joss.theoj.org/papers/10.21105/joss.11060) · [Project page](https://vectorinstitute.github.io/fairsense-agentix/) · [Code](https://github.com/VectorInstitute/fairsense-agentix) · [PyPI](https://pypi.org/project/fairsense-agentix/).
- :material-check-decagram: **SONIC-O1 accepted at EMNLP 2026 (Main)**. [Project page](https://vectorinstitute.github.io/sonic-o1/) · [Paper](https://aclanthology.org/2026.emnlp-main.767/) · [Code](https://github.com/VectorInstitute/sonic-o1) · [Leaderboard](https://huggingface.co/spaces/vector-institute/sonic-o1-leaderboard).
- :material-check-decagram: **DiagFlowBench accepted at EMNLP 2026 (Industry)**. [Paper](https://aclanthology.org/2026.emnlp-industry.108/).
- :material-check-decagram: **AgentFinVQA accepted at NeurIPS 2026 AABA4ET**. [Project page](https://vectorinstitute.github.io/AgentFinVQA/) · [Preprint](https://arxiv.org/abs/2606.19782) · [Code](https://github.com/VectorInstitute/AgentFinVQA/).
- :material-check-decagram: **Detecting Deception, Not Deepfakes accepted at NeurIPS 2026 TAE**. [Project page](https://jesseeho.github.io/deepfake-deception/) · [Preprint](https://arxiv.org/abs/2605.09007).

[:material-arrow-right: **View full list**](updates.md){ .md-button .md-button--primary }

---

## Related Projects

A snapshot of Vector's key contributions within AIXpert. Each project has its own repository, documentation, and quickstart.

<div class="grid cards" markdown>

-   :material-rocket-launch: **MARS**

    Two-path video detector for facial manipulation and fully generated video. A residual path reads spatial and temporal differences next to appearance, and a clip-level gate combines it with a semantic path. Across seven datasets it reaches 91.43% average AUROC, and it reports the frames and regions behind each decision.

    [:material-arrow-right: Project page](https://vectorinstitute.github.io/mars/) · [Preprint](https://arxiv.org/abs/2611.12508) · [Code](https://github.com/VectorInstitute/mars)

-   :material-database: **Mozaic**

    Audio-video deepfake benchmark with a four-way label: real or fake face, and real or fake voice. It asks which part is fake, what kind of manipulation, whose identity, and why. Zero-shot models catch fake video far more often than fake audio, and a held-out face-swap generator drops the best detector to 78.3%. Paper coming.

    [:material-arrow-right: Project page](https://vectorinstitute.github.io/mozaic/) · [Code](https://github.com/VectorInstitute/mozaic) · [Dataset](https://huggingface.co/datasets/vector-institute/Mozaic)

-   :material-scale-balance: **UnBias-Plus**

    AI-driven toolkit for bias detection and debiasing in text: biased spans, severity, reasoning, neutral replacements, and a full neutral rewrite for more trustworthy workflows.

    [:material-arrow-right: Project page](https://vectorinstitute.github.io/unbias-plus/) · [Code](https://github.com/VectorInstitute/unbias-plus) · [PyPI](https://pypi.org/project/unbias-plus/)

-   :material-leaf: **DIA (Data & Impact Accounting)**

    Open-source toolkit to track energy, water, and CO₂ impact of open-source AI models and their derivatives, with a public dashboard.

    [:material-arrow-right: Project page](https://vectorinstitute.github.io/ai-impact-accounting/) · [Code](https://github.com/VectorInstitute/ai-impact-accounting/) · [PyPI](https://pypi.org/project/ai-impact-accounting/) · [Dashboard](https://huggingface.co/spaces/vector-institute/dia-dashboard)

-   :material-shield-search: **FairSense-AgentiX**

    Agentic platform for fairness and AI-risk analysis on text, images, and datasets, published in JOSS. An agent plans each check, selects tools, critiques the result, and records the steps.

    [:material-arrow-right: Project page](https://vectorinstitute.github.io/fairsense-agentix/) · [Paper](https://joss.theoj.org/papers/10.21105/joss.11060) · [Code](https://github.com/VectorInstitute/fairsense-agentix) · [PyPI](https://pypi.org/project/fairsense-agentix/)

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

    [:material-arrow-right: Paper](https://aclanthology.org/2026.findings-acl.1968/) · [Project page](https://vectorinstitute.github.io/Factual-Preference-Alignment/) · [Code](https://github.com/VectorInstitute/Factual-Preference-Alignment)

-   :material-image-multiple: **HumaniBench**

    Fairness-focused vision-language benchmark evaluating foundation models across human-centric demographics.

    [:material-arrow-right: Project page](https://vectorinstitute.github.io/HumaniBench/) · [Paper](https://dl.acm.org/doi/10.1145/3845999)

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
