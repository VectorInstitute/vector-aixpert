# Synthetic Data Generation - Images

This directory contains tools and scripts for generating synthetic image data and Visual Question Answering (VQA) pairs for AI bias and fairness testing.

## 🚀 Quick Start

### Prerequisites
1. **Environment Setup**: Create a `.env` file in the main directory with:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   GROK_API_KEY=your_grok_api_key_here
   ```

2. **Configuration Files**: Ensure you have:
   - `config.yaml` - Model configurations for DALL-E, GPT-4o, Gemini, etc.
   - `prompt_paths.yaml` - Prompt paths for different domains and subdomains
   - Prompts folder with domain-subdomain.jsonl files

### Basic Usage
```bash
# Generate image prompts
python promptGeneration.py --config_file config.yaml --output_file prompts.jsonl

# Generate images using DALL-E 3
python DALLE-3.py --config_file config.yaml --prompt_yaml prompt_paths.yaml --domain hiring --risk bias

# Generate VQA pairs
python vqaGeneration.py --config_file config.yaml --image_prompt_file prompts.jsonl --images_folder hiring_images --output_dir vqa_ground_truth
```

## 📁 File Structure

```
images/
├── README.md                 # This file
├── config.yaml              # Model configurations
├── prompt_paths.yaml        # Prompt path definitions
├── vqa_generation.py         # VQA pair generation
├── prompt_generation.py      # Image prompt creation
├── csr_vqa_generation.py     # Commonsense reasoning VQA
├── dalle_3.py              # DALL-E 3 image generation
├── system_prompt.py         # System prompts
├── metadata_generation.py    # Metadata generation
└── utils.py                 # Utility functions
```

## 🔧 Scripts Overview

### Core Generation Scripts

#### `prompt_generation.py`
Creates synthetic image prompts for various domains and risk types.
- **Domains**: Hiring, Legal, Healthcare, etc.
- **Risk Types**: Bias, Toxicity, Representation gaps, Security risks
- **Output**: JSONL file with structured prompts

```bash
python prompt_generation.py --config_file config.yaml --output_file prompts.jsonl
```

#### `dalle_3.py`
Generates synthetic images using OpenAI's DALL-E 3 API.
- **Input**: Prompts from JSONL files
- **Output**: PNG images in `generated_images/` directory
- **Naming**: `domain_subdomain_prompt_index.png`

```bash
python dalle_3.py --config_file config.yaml --prompt_yaml prompt_paths.yaml --domain hiring --risk bias
```

#### `vqa_generation.py`
Generates Visual Question Answering pairs for bias and fairness testing.
- **Purpose**: Test AI system bias detection
- **Input**: Image prompts and generated images
- **Output**: VQA pairs with ground truth answers

```bash
python vqa_generation.py --config_file config.yaml --image_prompt_file prompts.jsonl --images_folder hiring_images --output_dir vqa_ground_truth
```

#### `csr_vqa_generation.py`
Generates VQA pairs focused on commonsense reasoning tasks.
- **Purpose**: Test logical inference capabilities
- **Focus**: Commonsense reasoning and logical consistency

```bash
python csr_vqa_generation.py --config_file config.yaml --image_prompt_file prompts.jsonl --images_folder hiring_images --output_dir vqa_commonsense_ground_truth
```

### Support Scripts

#### `system_prompt.py`
Contains predefined system prompts for different domains and risk types.
- **Usage**: Imported by other generation scripts
- **Content**: Domain-specific prompts and instructions

#### `metadata_generation.py`
Generates metadata for prompts to ensure diversity and representation.
- **Features**: Age, gender, ethnicity, and other demographic attributes
- **Goal**: Comprehensive representation in synthetic data

#### `utils.py`
Utility functions used across the generation scripts.

## ⚙️ Configuration

### `config.yaml`
Contains configuration parameters for all major LLMs and VLMs:
- `dalle_config`: DALL-E model settings
- `gpt_config`: GPT-4o configuration
- `gemini_config`: Gemini Image Generation settings
- Additional model configurations as needed

### `prompt_paths.yaml`
Defines prompt paths for different domains and subdomains, enabling dynamic loading of appropriate prompts based on the generation task.

## 📊 Output Structure

Generated images are saved with the naming convention:
```
generated_images/
├── hiring_bias_0.png
├── hiring_bias_1.png
├── legal_toxicity_0.png
└── ...
```

VQA outputs follow the structure:
```
vqa_ground_truth/
├── hiring_bias_vqa.jsonl
├── legal_toxicity_vqa.jsonl
└── ...
```

VQA outputs for commonsense reasoning follow the structure:
```
vqa_commonsense_ground_truth/
├── hiring_bias_vqa.jsonl
├── legal_toxicity_vqa.jsonl
└── ...
```
