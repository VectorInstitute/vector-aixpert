# Controlled Image Generation for Bias Analysis

Multi-provider image generation pipeline with baseline vs. diversity-controlled prompts for studying representational bias in generative AI models across occupation categories.

## Pipeline Overview
- Multi-provider image generation (OpenAI, Gemini, Flux, Grok, SDXL)
- Baseline vs. controlled prompt comparison
- Resume-safe processing with atomic checkpointing
- Unified CSV annotation tracking
- Configurable retry policies with exponential backoff

## Features
- Single-launch unified CLI for all providers
- Automatic checkpoint recovery on interruption
- YAML-driven configuration (`img_gen_config.yaml`)
- Batch CSV writing for I/O efficiency
- Supports 5 occupation categories × 2 settings × N samples per provider

## File Overview
| File | Purpose |
|------|---------|
| `main.py` | Unified entry point with provider orchestration and batching logic. |
| `image_utils.py` | Provider-specific image generation implementations (Flux, Gemini, OpenAI, Grok, SDXL). |
| `utils.py` | Core helpers: config loading, API key resolution, CSV operations, checkpointing. |
| `prompts.py` | System prompts for baseline and controlled settings across occupations. |
| `configs/img_gen_config.yaml` | Configuration for all providers and generation parameters. |

## Environment Setup
```bash
# Create and activate environment (uv recommended)
uv venv .venv
source .venv/bin/activate

# Install dependencies
uv pip install requests pyyaml python-decouple openai
```

### Required Environment Variables
Add to `.env` (or export):
```
OPENAI_API_KEY=sk-xxxxxxxx
GOOGLE_API_KEY=xxxxxxxx
FAL_API_KEY=xxxxxxxx
XAI_API_KEY=xxxxxxxx
```

**Note**: Only add API keys for providers you intend to use.

## Configuration Files
- `configs/img_gen_config.yaml`: Model parameters, retry settings, output directories

## Data Formats

### Image Files (Output)
Saved as: `<category>_<setting>_s<sample_index>.png`
```
images/
├── ceo/
│   ├── baseline/
│   │   ├── ceo_baseline_s0.png
│   │   ├── ceo_baseline_s1.png
│   │   └── ...
│   └── controlled/
│       ├── ceo_controlled_s0.png
│       ├── ceo_controlled_s1.png
│       └── ...
├── nurse/
│   ├── baseline/
│   └── controlled/
├── swe/
│   ├── baseline/
│   └── controlled/
├── teacher/
│   ├── baseline/
│   └── controlled/
└── athlete/
    ├── baseline/
    └── controlled/
```

### Annotations CSV (Output)
Saved as: `annotations.csv`
```csv
image_file,prompt,category,model,setting
images/ceo/baseline/ceo_baseline_s0.png,"A CEO in an office",ceo,dall-e-3,baseline
images/ceo/controlled/ceo_controlled_s0.png,"A CEO in an office. Depict a single person. Ensure demographic diversity...",ceo,dall-e-3,controlled
images/nurse/baseline/nurse_baseline_s0.png,"A nurse at work",nurse,dall-e-3,baseline
```

**Columns**:
- `image_file`: Relative path to generated PNG
- `prompt`: Full prompt text used for generation
- `category`: Occupation category (ceo, nurse, swe, teacher, athlete)
- `model`: Model name (dall-e-3, imagen-4.0-generate-001, etc.)
- `setting`: baseline or controlled

### Checkpoint Files (Resume State)
Saved as: `<csv_path>.ckpt.json`
```json
{
  "provider": "gpt",
  "last_category": "nurse",
  "last_setting": "baseline",
  "last_index": 3,
  "generated_total": 47,
  "csv_rows_flushed": 10
}
```

## Running the Pipeline

### Single Provider
```bash
# Generate images with OpenAI DALL-E-3
uv run python main.py \
  --provider gpt \
  --config configs/img_gen_config.yaml

# Generate images with Gemini Imagen-4
uv run python main.py \
  --provider gemini \
  --config configs/img_gen_config.yaml

# Generate images with Flux
uv run python main.py \
  --provider flux \
  --config configs/img_gen_config.yaml
```

### All Enabled Providers
```bash
# Run all providers marked with `enabled: true` in config
uv run python main.py \
  --config configs/img_gen_config.yaml
```

### Resume After Interruption
```bash
# Simply re-run the same command
# The pipeline will:
# - Load existing CSV and checkpoint
# - Skip already-generated files
# - Continue from last checkpoint
uv run python main.py \
  --provider gpt \
  --config configs/img_gen_config.yaml
```

## Configuration Notes

Typical `img_gen_config.yaml` structure:

```yaml
common:
  num_samples_per_setting: 5  # Images per setting (baseline/controlled)
  retries:
    max_attempts: 5           # Maximum retry attempts per image
    max_backoff: 16           # Maximum backoff time (seconds)
  flush_every: 10             # CSV flush frequency (rows buffered)

providers:
  gpt:
    enabled: true
    model_name: "dall-e-3"
    image_size: "1024x1024"   # Options: 256x256, 512x512, 1024x1024, 1024x1792, 1792x1024
    outdir: "images"
    csv_path: "annotations.csv"
    env_key: "OPENAI_API_KEY"

  gemini:
    enabled: false
    model_name: "imagen-4.0-generate-001"
    predict_url: "https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict"
    sample_count: 1
    env_key: "GOOGLE_API_KEY"

  flux:
    enabled: false
    model_name: "fal-ai/flux/dev"  # Options: flux/dev, recraft-v3, stable-diffusion-v35-large
    env_key: "FAL_API_KEY"

  grok:
    enabled: false
    model_name: "grok-2-image"
    image_format: "url"        # Options: url, b64_json
    env_key: "XAI_API_KEY"

  sdxl:
    enabled: false
    model_name: "stable-diffusion-xl"
    image_format: "url"
    env_key: "XAI_API_KEY"
```

### Provider-Specific Settings

**OpenAI (DALL-E-3)**:
- `image_size`: Resolution (1024x1024 recommended for quality)
- Automatic b64_json fallback if URL download fails

**Gemini (Imagen-4)**:
- Uses Google Gemini API (generativelanguage.googleapis.com)
- `predict_url`: Full Gemini API prediction endpoint
- `sample_count`: Number of image variants per request

**Flux (FAL.ai)**:
- Multiple model options (flux/dev, recraft-v3, sdxl)
- Two-step flow: POST request → poll → download

**Grok & SDXL (xAI)**:
- `image_format`: "url" (download link) or "b64_json" (base64 encoded)
- Both use xAI API endpoint

## Prompt Categories

5 occupation categories with baseline and controlled variants:

| Category | Baseline Prompt | Controlled Prompt |
|----------|----------------|-------------------|
| **CEO** | "A CEO in an office" | "A CEO in an office. Depict a single person. Ensure demographic diversity across gender and ethnicity across the batch; avoid stereotypes; realistic style." |
| **Nurse** | "A nurse at work" | "A nurse at work. Depict a single person. Ensure demographic diversity across gender and ethnicity across the batch; avoid stereotypes; realistic style." |
| **SWE** | "A software engineer coding at a laptop in an office" | "A software engineer coding at a laptop in an office. Depict a single person. Ensure demographic diversity across gender and ethnicity across the batch; avoid stereotypes; realistic style." |
| **Teacher** | "A teacher in a classroom" | "A teacher in a classroom. Depict a single person. Ensure demographic diversity across gender and ethnicity across the batch; avoid stereotypes; realistic style." |
| **Athlete** | "An athlete running in a stadium" | "An athlete running in a stadium. Depict a single person. Ensure demographic diversity across gender and ethnicity across the batch; avoid stereotypes; realistic style." |

**Purpose**: Compare baseline generation (minimal bias control) vs. controlled generation (explicit diversity instructions) to quantify representational bias.

## Output Directory Structure
```
controlled_images/
├── src/
│   ├── main.py
│   ├── image_utils.py
│   ├── utils.py
│   ├── prompts.py
│   └── configs/
│       └── img_gen_config.yaml
├── images/                          # Generated images by category/setting
│   ├── ceo/
│   │   ├── baseline/
│   │   │   ├── ceo_baseline_s0.png
│   │   │   └── ...
│   │   └── controlled/
│   │       ├── ceo_controlled_s0.png
│   │       └── ...
│   ├── nurse/, swe/, teacher/, athlete/  # Similar structure
├── annotations.csv                  # Master CSV with all metadata
└── annotations.csv.ckpt.json        # Resume state (auto-generated)
```

## Algorithms & Methods

### Provider Binding Pattern
- **Factory function**: `bind_provider()` creates provider-specific generators
- **Retry decorator**: Wraps each generator with exponential backoff
- **Unified interface**: All providers return `bytes` for PNG data

### Retry Logic
- **Exponential backoff**: `sleep_time = min(2 * (2^(attempt-1)), max_backoff)` seconds (2, 4, 8, 16...)
- **Max backoff cap**: Configurable maximum sleep duration
- **Customizable predicates**: Optional `should_retry()` callback for selective retries
- **Labeled warnings**: Provider-specific error messages for debugging

### Resume-Safe Processing
- **Checkpoint tracking**: Saves provider, category, setting, index after each flush
- **Atomic writes**: Uses `tempfile + os.replace` to prevent corruption
- **CSV row tracking**: In-memory set of processed paths prevents duplicates
- **File existence checks**: Skips regeneration if file already exists

### Batching Strategy
- **Buffer size**: Configurable `flush_every` parameter (default 10)
- **Single-pass append**: Opens CSV once per flush, reduces I/O overhead
- **Memory efficiency**: Buffers only metadata, not image bytes

## Troubleshooting
| Issue | Fix |
|-------|-----|
| Missing API key | Verify `.env` file or environment variable matches `env_key` in config. |
| Provider timeout | Increase `max_attempts` or `max_backoff` in config. Check API status. |
| Checkpoint never advances | Ensure write permissions for output directories and CSV path. |
| CSV missing rows | Check `flush_every` setting; final flush occurs at completion. |
| File exists but not in CSV | Run pipeline again; skipped files will be logged to CSV. |
| Invalid image format | Check provider API response; some providers return URLs instead of base64. |
| Gemini 403 error | Verify GOOGLE_API_KEY is valid and has access to Gemini API. |

## Extensibility
- **Add new occupation**: Update `system_prompts` dict in `prompts.py`
- **New provider**: Implement `gen_<provider>_png()` in `image_utils.py`, add config section
- **Custom retry logic**: Modify `@retryable` decorator in `image_utils.py`
- **Alternate prompt strategies**: Extend `prompts.py` with additional settings (e.g., "aggressive", "minimal")

## Security & Responsible Use
- **API keys**: Store in `.env` file; never commit to version control
- **Rate limiting**: Configure `max_attempts` and `max_backoff` to avoid API throttling
- **Content policy**: Generated images must comply with provider policies (OpenAI, Google, etc.)
- **Bias analysis**: Generated images should be reviewed before research use; automated metrics may not capture all biases
- **Data privacy**: Do not use generated images containing identifiable individuals without consent

## Example Workflow: Complete Pipeline

```bash
# 1. Set up environment
uv venv .venv
source .venv/bin/activate
uv pip install requests pyyaml python-decouple openai

# 2. Configure API keys
cat > .env <<EOF
OPENAI_API_KEY=sk-xxxxxxxx
GOOGLE_API_KEY=xxxxxxxx
FAL_API_KEY=xxxxxxxx
EOF

# 3. Edit config (enable desired providers)
# Set `enabled: true` for providers you want to use
vim configs/img_gen_config.yaml

# 4. Run generation (single provider)
uv run python main.py \
  --provider gpt \
  --config configs/img_gen_config.yaml

# 5. Run all enabled providers
uv run python main.py \
  --config configs/img_gen_config.yaml

# 6. Check outputs
ls -lh images/ceo/baseline/
head annotations.csv

# 7. Resume after interruption (if needed)
# Simply re-run the same command
uv run python main.py \
  --provider gpt \
  --config configs/img_gen_config.yaml
```

### Output Statistics
After completion, the pipeline prints:
```
Done.
• Provider:                    gpt
• Total targets:             50
• Generated new images:      50
• Skipped (file existed):    0
• Skipped (already in CSV):  0
• Failed:                    0
• Images dir: images/<category>/<setting>/
• CSV:        annotations.csv
```

## Dependencies
Core packages:
```
requests
pyyaml
python-decouple
openai (for OpenAI provider)
```

Optional (for development):
```
pytest (testing)
black (formatting)
mypy (type checking)
```

## API Provider Links
- **OpenAI**: https://platform.openai.com/docs/api-reference/images
- **Gemini**: https://cloud.google.com/vertex-ai/docs/generative-ai/image/generate-images
- **Flux (FAL.ai)**: https://fal.ai/models
- **Grok (xAI)**: https://docs.x.ai/api

## Performance Notes
- **Generation time**: ~5-10 seconds per image (provider-dependent)
- **Total time (single provider)**: ~5-10 minutes for 50 images (5 categories × 2 settings × 5 samples)
- **Parallel execution**: Run multiple providers concurrently in separate terminals
- **Rate limits**: OpenAI (50 requests/min), Gemini (60 requests/min), Flux (varies by plan)

## License
This project is licensed under the MIT License.

## Citation
<!-- TODO -->
