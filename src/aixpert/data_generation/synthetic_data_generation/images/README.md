# Synthetic Image & VQA Dataset Generation

Pipeline to generate synthetic image prompts, images, metadata, and Visual Question Answering (VQA / CSR‑VQA) pairs across domain–risk dimensions for Responsible AI evaluation.

## Contents
- Prompt generation (LLM JSON objects)
- Image synthesis (Gemini / DALL‑E 3)
- Metadata extraction (demographics)
- VQA (risk + commonsense variants)
- Checkpointed, resume‑safe processing

## Features
- Multi‑stage CLI (`main.py` subcommands)
- Modular standalone scripts (`prompt_generation.py`, `gemini.py`, `dalle_3.py`, `metadata_generation.py`, `vqa_generation.py`, `csr_vqa_generation.py`)
- Automatic checkpointing per stage
- YAML‑driven configuration (`config.yaml`, `prompt_paths.yaml`)
- Supports multiple domains & risk categories

## File Overview
| File | Purpose |
|------|---------|
| `main.py` | Unified entry point with subcommands for all stages. |
| `system_prompt.py` | Houses structured system prompts families (image, metadata, VQA). |
| `utils.py` | Core helpers: load config, load prompts, OpenAI + Gemini calls, checkpoint I/O. |
| `prompt_generation.py` | Generates prompt JSON objects (image prompts). |
| `gemini.py` / `dalle_3.py` | Image synthesis via Gemini or DALL‑E 3. |
| `metadata_generation.py` | Generates demographic metadata from image prompts. |
| `vqa_generation.py` | Risk‑focused VQA generation with image context. |
| `csr_vqa_generation.py` | Commonsense reasoning VQA variant. |
| `system_utils.py` | Orchestrated stage implementations used by `main.py`. |
| `prompt_paths.yaml` | Maps domain + risk → JSONL prompt files. |

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
- prompt_paths.yaml: Domain/risk routing to prompt JSONL files (pre‑seeded or generated in Stage 1)

## Data Formats

### Prompt JSONL (output of Stage 1)
Each line:
```json
{
  "domain": "hiring",
  "risk": "toxicity",
  "image_prompt": "A job interview setting..."
}
```

### Image Files (Stage 2)
Saved as: `<domain>_<risk>_image_<index>.png` in `<domain>_<risk>_images/`.

### Metadata JSONL (Stage 3)
```json
{
  "domain": "hiring",
  "risk": "toxicity",
  "image_prompt": "A job interview setting...",
  "image_path": "hiring-toxicity_images/hiring-toxicity_image_1.png",
  "metadata": {
    "age": ["young", "older"],
    "gender": ["male"],
    "ethnicity": ["Asian", "White"]
  }
}
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
  "image_path": "hiring-toxicity_images/hiring-toxicity_image_1.png",
  "metadata": { ... }  // carried forward if available
}
```

## Running the Pipeline (Unified)
Use main.py subcommands:

```bash
# Stage 1: Generate prompts
uv run main.py prompt_generation \
  --config_file ../../config.yaml \
  --prompt_yaml prompt_paths.yaml \
  --domain hiring --risk security_risks \
  --output_file hiring-security_risks.jsonl

# Stage 2: Generate images
uv run main.py image_generation \
  --config_file ../../config.yaml \
  --prompt_yaml prompt_paths.yaml \
  --domain hiring --risk security_risks

# Stage 3: Generate metadata
uv run main.py metadata_generation \
  --config_file ../../config.yaml \
  --prompt_variant v1 \
  --domain hiring --risk security_risks \
  --prompt_yaml prompt_paths.yaml \
  --images_folder hiring-security_risks_images/ \
  --output_dir metadata_ground_truth/ \
  --output_file hiring-security_risks_metadata.jsonl

# Stage 4a: Commonsense VQA
uv run main.py csr-vqa_generation \
  --config_file ../../config.yaml \
  --prompt_domain csr --prompt_variant simple \
  --domain hiring --risk security_risks \
  --image_prompt_file metadata_ground_truth/hiring-security_risks_metadata.jsonl \
  --images_folder hiring-security_risks_images/ \
  --output_dir vqa_commonsense_ground_truth/ \
  --output_file hiring-security_risks_csr_vqa.jsonl

# Stage 4b: Risk VQA
uv run main.py vqa_generation \
  --config_file ../../config.yaml \
  --prompt_domain risk --prompt_variant v1 \
  --domain hiring --risk security_risks \
  --image_prompt_file metadata_ground_truth/hiring-security_risks_metadata.jsonl \
  --images_folder hiring-security_risks_images/ \
  --output_dir vqa_ground_truth/ \
  --output_file hiring-security_risks_vqa.jsonl
```

### Run All (if extended)
If `all_stages` is configured:
```bash
uv run main.py all_stages \
  --config_file ../../config.yaml \
  --prompt_yaml prompt_paths.yaml \
  --domain hiring \
  --risk security_risks
```
(Requires alignment of arguments; may need enhancement to include risk.)

## Standalone Scripts
You can also invoke individual stage scripts:
```bash
# Stage 1
uv run prompt_generation.py --config_file ../../config.yaml --domain hiring --risk security_risks --prompt_yaml prompt_paths.yaml --output_dir prompts/ --output_file hiring-security_risks.jsonl

# Stage 2
uv run gemini.py --config_file ../../config.yaml --prompt_yaml prompt_paths.yaml --domain hiring --risk security_risks

# Stage 3
uv run metadata_generation.py --config_file ../../config.yaml --prompt_variant v1 --domain hiring --risk security_risks --prompt_yaml prompt_paths.yaml --images_folder hiring-security_risks_images/ --output_dir metadata_ground_truth/ --output_file hiring-security_risks_metadata.jsonl

# Stage 4a
uv run vqa_generation.py --config_file ../../config.yaml --prompt_domain risk --prompt_variant v1 --domain hiring --risk security_risks --image_prompt_file metadata_ground_truth/hiring-security_risks_metadata.jsonl --images_folder hiring-security_risks_images/ --output_dir vqa_ground_truth/ --output_file hiring-security_risks_vqa.jsonl

# Stage 4b
uv run csr_vqa_generation.py --config_file ../../config.yaml --prompt_domain csr --prompt_variant simple --domain hiring --risk security_risks --image_prompt_file metadata_ground_truth/hiring-security_risks_metadata.jsonl --images_folder hiring-security_risks_images/ --output_dir vqa_commonsense_ground_truth/ --output_file hiring-security_risks_csr_vqa.jsonl
```

## Checkpointing & Resume
Each generation stage writes a checkpoint file:
- Metadata: `checkpoint_metadata_<domain>-<risk>.txt`
- VQA: `checkpoint_vqa_<domain>-<risk>.txt`
- CSR‑VQA: `checkpoint_csr_vqa_<domain>_<risk>.txt`

Behavior:
- load_checkpoint() returns last processed index or `-1`.
- Loop resumes from `last_index + 1`.
- Checkpoint only updated after successful save.

To resume after interruption, rerun the same command; already completed items are skipped.

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
<!-- Add MIT License -->
This project is licensed under the MIT License.

## Citation
<!-- TODO -->
