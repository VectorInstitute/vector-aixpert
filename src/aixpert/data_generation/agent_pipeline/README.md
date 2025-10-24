# Agentic Synthetic Image & VQA Generation

Agentic Pipeline using agents, tasks and flows to generate synthetic image prompts, images, metadata, and Visual Question Answering (VQA / CSR‑VQA) pairs across domain–risk dimensions for Responsible AI evaluation.

## Pipeline Overview
- Prompt generation (LLM JSON objects)
- Image synthesis (Gemini / DALL‑E 3)
- Metadata extraction (demographics)
- VQA (risk + commonsense variants)

## Features
- Single‑launch agentic pipeline using crewai for running multistage synthetic datageneration
- YAML‑driven configuration (`config.yaml`)
- Supports multiple domains & risk categories

## File Overview
| File | Purpose |
|------|---------|
| `crew_orchestrate.py` | Unified entry point with subcommands for all stages. |
| `system_prompt.py` | Houses system prompts families (image, metadata, VQA). |
| `utils.py` | Core helpers: load config, load prompts, check_last_index, read_directory, var_to_dict_prompts. |
| `flows/image_generation_flow.py` | Flow for Generating images based on the model. |
| `flows/vqa_generation_flow.py` | Flow for generating VQA (Visual Question Answering) data. |
| `llm_factory.py` | Responsible for initializing the text llm to be used. |
| `load_text_llm.py` | Returns a text llm to be used by crewai. |
| `agent.py` | Houses crewai agents and tasks for different stages. |
| `custom_llm.py` | File for defining a custom llm. |

## Environment Setup
```bash
# Create and activate environment (uv recommended)
uv venv .venv
source .venv/bin/activate

# Install base + optional doc groups (if defined in pyproject.toml)
uv sync
```

### Required Environment Variables
Add to .env (or export):
```
OPENAI_API_KEY=xxxxxxxx
GEMINI_API_KEY=xxxxxxxx
```

## Configuration Files
- config.yaml: Model and generation parameters (sections: `gpt`, `gemini`, `dalle`)

## Data Formats

### Prompt Generation (output of Stage 1)
```json
{
  "domain": "hiring",
  "risk": "toxicity",
  "image_prompt": "A job interview setting..."
}
```

### Image Files (Stage 2)
Saved as: `<domain>_<risk>_image_<index>.png` in `./images/<llm>/<domain>_<risk>_images/`.

### Metadata JSONL (Stage 3)
save
```json
{
  "domain": "hiring",
  "risk": "toxicity",
  "image_prompt": "A job interview setting...",
  "image_path": "hiring_toxicity_images/hiring_toxicity_image_1.png",
  "metadata": {
    "age": ["young", "older"],
    "gender": ["male"],
    "ethnicity": ["Asian", "White"]
  }
}
Saved as: `<domain>_<risk>_metadata.jsonl` in `./metadata/<llm>/`.
```

### VQA / CSR‑VQA JSONL (Stage 4)
```json
{
  "domain": "hiring",
  "risk": "toxicity",
  "vqa": [
    {
      "question": "...",
      "answer": "...",
      "rationale": "..."
    }
  ],
  "image_prompt": "A job interview setting...",
  "image_path": "hiring_toxicity_images/hiring_toxicity_image_1.png",
  "metadata": { ... }  // carried forward if available
}
```
saved as Saved as: `<domain>_<risk>_vqa.jsonl` in `vqa/<llm>/<vqa_prompt_type>/`.

## Running the Pipeline (Unified)
Use crew_orchestrate.py to run the complete pipeline:

```bash
uv run crew_orchestrate.py --llm [openai,gemini]



## Configuration Notes
Typical config.yaml sections:
```yaml
gpt:
  model: gpt-4o
  batch_size: 1
  max_tokens: 2048
  temperature: 0.7

gemini:
  model: imagen-4.0-generate-001
  numberOfImages: 1
  sampleImageSize: 1024x1024
  aspectRatio: 1:1
  personGeneration: ALLOW_ALL

dalle:
  model: dall-e-3
  quality: standard
  style: vivid
  img_size: 1024x1024
```

## Extensibility
- Add new domain/risk: update prompt_paths.yaml + system_prompt.py.
- Alternate models: adjust config.yaml sections.
- New stage: implement in system_utils.py, register subcommand in main.py.

## Troubleshooting
| Issue | Fix |
|-------|-----|
| Missing API key | Verify .env or environment export. |
| Checkpoint never advances | Ensure exceptions are logged; confirm write permissions. |
| Invalid JSON lines | Prompts may contain partial JSON; regex extraction preserves valid objects. |
| Image file missing in VQA stage | Verify Stage 2 folder name matches `<domain>_<risk>_images`. |

## Security & Responsible Use
Synthetic data should be reviewed for plausibility and unintended sensitive content. Demographic inference is heuristic; validate before downstream use.

## License
This project is licensed under the MIT License.

## Citation
<!-- TODO -->
