"""Script to generate prompts for synthetic images using GPT-4o."""

# Standard library imports
import argparse
import json
import os
import re
import sys
from pathlib import Path

import yaml
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
        "--prompt_yaml",
        type=str,
        default="prompt_params.yaml",
        help="YAML file containing prompt parameters",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="prompts",
        help="Directory to save output files",
    )
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
    prompt_yaml = args.prompt_yaml

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
    output_dir = args.output_dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_jsonl_path = os.path.join(output_dir, args.output_file)
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

    try:
        with open(prompt_yaml, "r", encoding="utf-8") as f:
            prompt_paths = yaml.safe_load(f) or {}
    except FileNotFoundError:
        prompt_paths = {}

    # Ensure structure
    prompt_paths.setdefault("prompts", {}).setdefault(domain, {})

    # Update or add mapping to the exact output_jsonl_path you’re using
    prompt_paths["prompts"][domain][risk] = output_jsonl_path

    # Write back without reordering keys
    with open(prompt_yaml, "w", encoding="utf-8") as f:
        yaml.safe_dump(prompt_paths, f, sort_keys=False)

    print(
        f"Recorded mapping in {prompt_yaml}: prompts.{domain}.{risk} -> {output_jsonl_path}"
    )

    print("Prompts generation completed successfully.")


if __name__ == "__main__":
    main()
