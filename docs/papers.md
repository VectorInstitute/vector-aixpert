# Papers

Selected publications and preprints from the AIXpert project. Each entry links to arXiv (or equivalent) where available.

---

## AIXpert project papers

### From Features to Actions: Explainability in Traditional and Agentic AI Systems

**Paper** · <a href="https://arxiv.org/abs/2602.06841" target="_blank" rel="noopener"><img src="https://img.shields.io/badge/arXiv-B31B1B?style=flat-square&amp;logo=arxiv&amp;logoColor=white" alt="arXiv"></a> **Code** · <a href="https://github.com/VectorInstitute/unified-xai-evaluation-framework" target="_blank" rel="noopener"><img src="https://img.shields.io/badge/GitHub-181717?style=flat-square&amp;logo=github&amp;logoColor=white" alt="GitHub"></a> **Project** · <a href="https://vectorinstitute.github.io/unified-xai-evaluation-framework/" target="_blank" rel="noopener"><img src="https://img.shields.io/badge/Project_page-0F7DC2?style=flat-square" alt="Project"></a>

**Authors:** Sindhuja Chaduvula, Jessee Ho, Kina Kim, Aravind Narayanan, Mahshid Alinoori, Muskan Garg, Dhanesh Ramachandram, Shaina Raza.

Compares attribution-based explanations (SHAP, LIME) with trace-based diagnostics across static and agentic settings. Attribution is stable for static prediction (Spearman ρ = 0.86) but fails to diagnose agentic failures; trace-grounded rubrics localize breakdowns (e.g. state-tracking inconsistency 2.7× more in failed runs, −49% success), motivating trajectory-level explainability for agentic systems.

### SONIC-O1: A Real-World Benchmark for Evaluating Multimodal Large Language Models on Audio-Video Understanding

**Paper** · <a href="https://arxiv.org/abs/2601.21666" target="_blank" rel="noopener"><img src="https://img.shields.io/badge/arXiv-B31B1B?style=flat-square&amp;logo=arxiv&amp;logoColor=white" alt="arXiv"></a> **Code** · <a href="https://github.com/VectorInstitute/sonic-o1" target="_blank" rel="noopener"><img src="https://img.shields.io/badge/GitHub-181717?style=flat-square&amp;logo=github&amp;logoColor=white" alt="GitHub"></a> **Dataset** · <a href="https://huggingface.co/datasets/vector-institute/sonic-o1" target="_blank" rel="noopener"><img src="https://img.shields.io/badge/Hugging_Face-FFD21E?style=flat-square&amp;logo=huggingface&amp;logoColor=000" alt="Hugging Face"></a> **Leaderboard** · <a href="https://huggingface.co/spaces/vector-institute/sonic-o1-leaderboard" target="_blank" rel="noopener"><img src="https://img.shields.io/badge/Leaderboard-FFD21E?style=flat-square&amp;logo=huggingface&amp;logoColor=000" alt="Leaderboard"></a>

**Authors:** Ahmed Y. Radwan, Christos Emmanouilidis, Hina Tabassum, Deval Pandya, Shaina Raza.

SONIC-O1, a fully human-verified real-world audio-video benchmark with 4,958 annotations across 13 conversational domains. We evaluate multimodal models on video summarization, evidence-grounded QA, and temporal event localization, and release an extensible evaluation suite to support reproducible benchmarking and robustness analysis.

### Reducing Hallucinations in LLMs via Factuality-Aware Preference Learning

**Paper** · <a href="https://arxiv.org/abs/2601.03027" target="_blank" rel="noopener"><img src="https://img.shields.io/badge/arXiv-B31B1B?style=flat-square&amp;logo=arxiv&amp;logoColor=white" alt="arXiv"></a> **Code** · <a href="https://github.com/VectorInstitute/Factual-Preference-Alignment" target="_blank" rel="noopener"><img src="https://img.shields.io/badge/GitHub-181717?style=flat-square&amp;logo=github&amp;logoColor=white" alt="GitHub"></a> **Dataset** · <a href="https://huggingface.co/datasets/vector-institute/Factuality_Alignment" target="_blank" rel="noopener"><img src="https://img.shields.io/badge/Hugging_Face-FFD21E?style=flat-square&amp;logo=huggingface&amp;logoColor=000" alt="Hugging Face"></a>

**Authors:** Sindhuja Chaduvula, Ahmed Y. Radwan, Azib Farooq, Yani Ioannou, Shaina Raza.

Preference-learning method (F-DPO) that targets factuality directly, improving factuality scores while reducing hallucination rates across multiple open-weight LLMs.

### Transparency in Agentic AI: A Survey of Interpretability, Explainability, and Governance

**Paper** · <a href="https://doi.org/10.31224/6451" target="_blank" rel="noopener"><img src="https://img.shields.io/badge/DOI-0F7DC2?style=flat-square" alt="DOI"></a> **Project** · <a href="https://vectorinstitute.github.io/Agentic-Transparency/" target="_blank" rel="noopener"><img src="https://img.shields.io/badge/Project_page-0F7DC2?style=flat-square" alt="Project"></a>

**Authors:** Shaina Raza, Ahmed Y. Radwan, Sindhuja Chaduvula, Mahshid Alinoori, Christos Emmanouilidis.

Agentic AI systems—LLM-based agents with planning, memory, and tool use—introduce transparency challenges that are poorly served by explainability methods designed for single-step predictions. This article surveys and synthesizes interpretability and explainability techniques relevant to agentic behavior across the agent lifecycle, organized using a five-axis taxonomy: cognitive objects being inspected, assurance objectives being targeted, mechanisms employed, lifecycle stages, and stakeholders served.

---

### Bias in the Picture: Benchmarking VLMs with Social-Cue News Images and LLM-as-Judge Assessment

**Paper** (NeurIPS 2025 LLM-eval Workshop) · <a href="https://arxiv.org/abs/2509.19659" target="_blank" rel="noopener"><img src="https://img.shields.io/badge/arXiv-B31B1B?style=flat-square&amp;logo=arxiv&amp;logoColor=white" alt="arXiv"></a> **Code** · <a href="https://github.com/VectorInstitute/bias-in-the-picture-benchmark" target="_blank" rel="noopener"><img src="https://img.shields.io/badge/GitHub-181717?style=flat-square&amp;logo=github&amp;logoColor=white" alt="GitHub"></a>

**Authors:** Aravind Narayanan, Vahid Reza Khazaie, Shaina Raza.

Benchmarking vision-language models with social-cue news images and LLM-as-judge assessment.

---

### TRiSM for Agentic AI: A Review of Trust, Risk, and Security Management in LLM-based Agentic Multi-Agent Systems

**Paper** · <a href="https://arxiv.org/abs/2506.04133" target="_blank" rel="noopener"><img src="https://img.shields.io/badge/arXiv-B31B1B?style=flat-square&amp;logo=arxiv&amp;logoColor=white" alt="arXiv"></a>

**Authors:** Shaina Raza, Ranjan Sapkota, Manoj Karkee, Christos Emmanouilidis.

A review of trust, risk, and security management (TRiSM) in LLM-based agentic and multi-agent systems.

---

### Responsible Agentic Reasoning and AI Agents—A Critical Survey

**Paper** (TechRxiv) · <a href="https://www.techrxiv.org/users/574774/articles/1329333-responsible-agentic-reasoning-and-ai-agents-a-critical-survey" target="_blank" rel="noopener"><img src="https://img.shields.io/badge/Paper-0F7DC2?style=flat-square" alt="Paper"></a>

**Authors:** Shaina Raza (Vector Institute), Ranjan Sapkota, Manoj Karkee (Cornell University), Christos Emmanouilidis (University of Groningen).

Critical survey of responsible agentic reasoning and AI agents.

---

### Evaluating and Regulating Agentic AI: A Study of Benchmarks, Metrics and Regulation

**Paper** (TechRxiv) · <a href="https://www.techrxiv.org/users/985444/articles/1350845-evaluating-and-regulating-agentic-ai-a-study-of-benchmarks-metrics-and-regulation" target="_blank" rel="noopener"><img src="https://img.shields.io/badge/Paper-0F7DC2?style=flat-square" alt="Paper"></a> **Code** · <a href="https://github.com/itsazibfarooq/agenticEvaluation" target="_blank" rel="noopener"><img src="https://img.shields.io/badge/GitHub-181717?style=flat-square&amp;logo=github&amp;logoColor=white" alt="GitHub"></a>

**Authors:** Azib Farooq, Shaina Raza, Nazmul Karim, Hasan Iqbal, Athanasios V. Vasilakos, Christos Emmanouilidis.

Reviews recent progress in developing and assessing agentic AI along three dimensions: benchmarks, metrics, and governance. Analyzes how evaluation frameworks capture reasoning, planning, collaboration, and ethical alignment in single- and multi-agent systems. Aims to establish a unified foundation for trustworthy, auditable, and human-aligned AI agents.

---

<!-- Reusable badge icons (shields.io, Simple Icons). Use in HTML: <a href="URL" target="_blank" rel="noopener"><img src="BADGE_URL" alt="..."></a>
  arXiv:  https://img.shields.io/badge/arXiv-B31B1B?style=flat-square&logo=arxiv&logoColor=white
  GitHub: https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white
  Hugging Face: https://img.shields.io/badge/Hugging_Face-FFD21E?style=flat-square&logo=huggingface&logoColor=000
-->
