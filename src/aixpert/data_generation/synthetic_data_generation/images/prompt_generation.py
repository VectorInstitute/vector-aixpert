"""Script to generate prompts for synthetic images using GPT-4o."""

# Standard library imports
import argparse
import json
import os
import re
import sys
from pathlib import Path

from decouple import AutoConfig

# Local utility functions for configuration and prompt generation
from utils import generate_prompts_with_userprompt, load_config


# Ensure local modules are importable
sys.path.append(os.path.dirname(__file__))
from system_prompt import image_prompt_generation


PROJECT_ROOT = Path(__file__).resolve().parents[5]
config = AutoConfig(search_path=str(PROJECT_ROOT))


def get_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate prompts for synthetic images using GPT-4o."
    )
    parser.add_argument(
        "--config_file", type=str, required=True, help="Path to the configuration file"
    )
    parser.add_argument(
        "--domain",
        type=str,
        choices=["hiring", "legal", "healthcare"],
        required=True,
        help="Domain for which to generate prompts",
    )
    parser.add_argument(
        "--risk",
        type=str,
        required=True,
        help="Risk category for the prompts (e.g., bias_v1, toxicity etc. based on the system prompt file)",
    )
    # The system_prompt_path argument is commented out; ignoring for now
    # parser.add_argument('--system_prompt_path',
    #                     type=str, required=True,
    #                     help='Path to the system prompt file')
    parser.add_argument(
        "--output_file",
        type=str,
        default="prompts.jsonl",
        help="File to save generated prompts",
    )
    return parser.parse_args()


def main() -> None:
    """Generate prompts and save them to a file."""
    # Parse arguments and load configuration
    args = get_arguments()
    yaml_config = load_config(args.config_file)

    # Ensure the OpenAI API key is provided via environment variable
    api_key = config("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    print("Using OpenAI API Key from environment variable.")

    # Retrieve model parameters from configuration
    model = yaml_config["gpt"].get("model", "gpt-4o")  # Model choice
    batch_size = yaml_config["gpt"].get("batch_size", 5)  # Batch size for processing
    max_tokens = yaml_config["gpt"].get("max_tokens", 2048)  # Max tokens for response
    temperature = yaml_config["gpt"].get(
        "temperature", 0.7
    )  # Temperature for response variability
    print(
        f"Using model: {model}, batch size: {batch_size}, max tokens: {max_tokens}, temperature: {temperature}"
    )

    # Select the system prompt to be used for generating prompts
    domain = args.domain
    risk = args.risk
    system_prompt = image_prompt_generation[domain][risk]
    print(f"Using system prompt:\n{system_prompt}")

    # Generate prompts using the provided system prompt and OpenAI API key
    prompts = generate_prompts_with_userprompt(
        system_prompt, api_key, model, batch_size, max_tokens, temperature
    )

    output_jsonl_path = args.output_file
    print(f"Saving prompts to {output_jsonl_path}")

    # Process the output prompts
    content = "\n".join(prompts) if isinstance(prompts, list) else prompts
    # Extract individual JSON objects using regex
    json_objects = re.findall(r"\{[^}]*\}", content, re.DOTALL)

    # Write the valid JSON objects line-by-line into the output file
    with open(output_jsonl_path, "w", encoding="utf-8") as f:
        for obj_str in json_objects:
            try:
                obj = json.loads(obj_str)
                json_line = json.dumps(obj, ensure_ascii=False)
                f.write(json_line + "\n")
            except json.JSONDecodeError as e:
                print(f"Skipping invalid JSON: {e}")

    print("Prompts generation completed successfully.")


if __name__ == "__main__":
    main()

# To run the script, use a command like:
# uv run prompt_generation.py --config_file path/to/config.yaml \
# --domain hiring \
# --risk bias_v1 \
# --output_file prompts.jsonl
