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

- :material-check-decagram: **TRiSM for Agentic AI accepted** — Paper accepted at [AI Open, Elsevier 2026](https://doi.org/10.1016/j.aiopen.2026.02.006). A review of trust, risk, and security management in LLM-based agentic multi-agent systems.
- :material-presentation: **Remarkable 2026** — We presented AIXpert projects at Remarkable 2026 ([photos on Updates](updates.md)).
- :material-robot: **SONIC-O1 Multi-Agent** — Multi-agent framework for audio-video understanding: planning, chain-of-thought reasoning, self-reflection, and temporal grounding with Qwen3-Omni. [Code](https://github.com/VectorInstitute/sonic-o1-agent).
- :material-file-document: **From Features to Actions** — Paper: [_Explainability in Traditional and Agentic AI Systems_](https://arxiv.org/abs/2602.06841) (arXiv). [Code](https://github.com/VectorInstitute/unified-xai-evaluation-framework) · [Project page](https://vectorinstitute.github.io/unified-xai-evaluation-framework/).
- :material-book-open-variant: **Transparency in Agentic AI** — Survey: [_Interpretability, Explainability, and Governance_](https://doi.org/10.31224/6451) (EngrXiv). [Project page](https://vectorinstitute.github.io/Agentic-Transparency/).
- :material-newspaper: **AIXpert news** — Our work was highlighted on the [AIXpert project website](https://aixpert-project.eu/2026/01/28/advancing-trustworthy-explainable-and-responsible-ai-at-neurips-2025/): *Advancing Trustworthy, Explainable, and Responsible AI at NeurIPS 2025* (Bias in the Picture, HumaniBench, Carbon Literacy, and more).
- :material-play-circle: **SONIC-O1** — Paper: [_A Real-World Benchmark for Evaluating MLLMs on Audio-Video Understanding_](https://arxiv.org/abs/2601.21666) (arXiv). [Dataset](https://huggingface.co/datasets/vector-institute/sonic-o1) · [Code](https://github.com/VectorInstitute/sonic-o1) · [Leaderboard](https://huggingface.co/spaces/vector-institute/sonic-o1-leaderboard).

[:material-arrow-right: **View full list**](updates.md){ .md-button .md-button--primary }

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

> Have feedback or want to contribute? See the [:material-account-group: Team](team.md) page and open an issue or pull request.