# Synthetic NLP Dataset Generation

Pipeline to generate synthetic data: Scene, MCQs and answer generation for pairs across domain–risk dimensions for Responsible AI evaluation.

## Contents
- User prompt generation
- MCQ generation with 3-4 options
- Open and close ended answer generation
- Checkpointed, resume‑safe processing

## Features
- Multi‑stage CLI (`main.py` subcommands)
- Automatic checkpointing per stage
- YAML‑driven configuration (`config.yaml`)
- Supports multiple domains & risk categories

## File Overview
| File | Purpose |
|------|---------|
| `main.py` | Unified entry point with subcommands for all stages. |
| `prompts.py` | Houses structured system prompts families (scenes, MCQ, answer). |
| `prompt_template.py` | User prompt templates. |
| `prompt_gen_utils.py` | Utility functions to create user prompts from templates. |
| `utils.py` | Core helpers: Decorators, OpenAI API, shuffle options, checkpoint I/O. |
| `schema.py` | JSON schema for OpenAI responses per stage. |
| `config.yaml` | Configuration to run pipeline. |
| `postprocess.py` | Postprocessing script for answer generation |

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
```

## Configuration Files
- config.yaml: OpenAI Model and file path parameters

## Data Formats

### Prompts (output of Stage 1)
Each line:
```json
[
  "List of user prompts",
]
```

### Scenes Files (Stage 2)
Saved as: `scenes_<domain>_<risk>.json`.
```json
{
  "id": "hiring",
  "prompt": "toxicity",
  "text": "A toxic job interview setting..."
}
```

### MCQs File (Stage 3)
Saved as: `mcqs_<domain>_<risk>.json`.

```json
{
  "id": "hiring",
  "prompt": "toxicity",
  "text": "A toxic job interview setting...",
  "MCQ: : MCQ": "How toxic is this scenario?",
  "A": "Very Toxic",
  "B": "Somewhat Toxic",
  "C": "Neutral",
  "D": "Not Very Toxic",
  "E": "Not Toxic",
}
```

### Answers File (Stage 4)
```json
{
  "id": "hiring",
  "prompt": "toxicity",
  "text": "A toxic job interview setting...",
  "MCQ: : MCQ": "How toxic is this scenario?",
  "A": "Very Toxic",
  "B": "Somewhat Toxic",
  "C": "Neutral",
  "D": "Not Very Toxic",
  "E": "Not Toxic",
  "answer": "Correct Option",
  "explanation": "Open ended explanation",
  "phrases": "List of toxic phrases"
}
```

## Running the Pipeline (Unified)
Use main.py subcommands:

```bash
# Stage 1: Generate user prompts
uv run main.py  \
  --config config.yaml \
  --stage user_prompt_gen

# Stage 2: Generate scees
uv run main.py  \
  --config config.yaml \
  --stage only_scenes

# Stage 3: Generate MCQs
uv run main.py  \
  --config config.yaml \
  --stage only_mcqs

# Stage 4: Generate Answers
uv run main.py  \
  --config config.yaml \
  --stage only_answers

### Run All (if extended)
If `all` is configured:
```bash
uv run main.py \
  --config config.yaml \
  --stage all
```

## Postprocessing
```bash
uv run postprocess.py \
  --data_path "path to answers_<domain>_<risk>.json" \
  --output_path "output_filename.json"
```

## Checkpointing & Resume
- Each generation stage writes a checkpoint file:
- Scenes: `checkpoints/checkpoints_<domain>_<risk>_<idx>.json`
- MCQs: `checkpoints/mcqs_<domain>_<risk>_<idx>.json`
- Answers: `checkpoints/answers_<domain>_<risk>_<idx>.json`

Behavior:
- load_checkpoint() returns the dictionary of the last stored file(based on a higher number) .
- Stores checkpoints after every 10 data points.

To resume after interruption, rerun the same command; already completed items are skipped.

## Configuration Notes
Typical config.yaml sections:
```yaml
repository: <path_to_repo>
#Model parameters
model: gpt-4o-mini #gpt-4o
max_output_tokens: 800
temperature: 1.2


domain: hiring
risk: bias_discrimination #Choose from: bias_discrimination, toxicity, representation_gaps, security_risks

user_prompts_file: prompts/hiring_bias_discrimination.json
user_prompts_save: prompts/scenes_hiring_bias_discrimination.json
mcq_data_file: prompts/mcqs_bias_discrimination.json
scenes_file: prompts/scenes_hiring_bias_discrimination.json
answers_file: prompts/answers_hiring_bias_discrimination.json

checkpoint_dir: checkpoints
```

## Extensibility
- Add new domain/risk: update prompt_template.yaml + prompts.py.
- Alternate models: Replace in config.yaml.
- New stage: implement in main.py, prompt_gen_utils.py.

## Troubleshooting
| Issue | Fix |
|-------|-----|
| Missing API key | Verify .env or environment export. |
| Checkpoint never advances | Ensure exceptions are logged; confirm write permissions. |
| Invalid JSON | Prompts may contain partial JSON; |

## Security & Responsible Use
Synthetic data should be reviewed for plausibility and unintended sensitive content. Demographic inference is heuristic; validate before downstream use.

## License
<!-- Add MIT License -->
This project is licensed under the MIT License.

## Citation
<!-- TODO -->
