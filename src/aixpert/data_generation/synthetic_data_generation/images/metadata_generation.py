"""Metadata Generation from Image Prompts."""

# Standard library imports
import argparse
import json
import os
import re
import sys
from pathlib import Path

from decouple import AutoConfig

# Third-party imports
from utils import (
    generate_prompts_without_image,
    load_checkpoint,
    load_config,
    save_checkpoint,
)


# Local imports
sys.path.append(os.path.dirname(__file__))
from system_prompt import metadata_prompt


PROJECT_ROOT = Path(__file__).resolve().parents[5]
config = AutoConfig(search_path=str(PROJECT_ROOT))


def process_image_prompt_metadata(
    image_prompt: str,
    system_prompt: str,
    api_key: str,
    model: str,
    batch_size: int,
    max_tokens: int,
    temperature: float,
) -> dict | None:
    """Generate metadata for a single image prompt."""
    prompts = generate_prompts_without_image(
        system_prompt, image_prompt, api_key, model, batch_size, max_tokens, temperature
    )

    # Combine prompts into a single string if it's a list.
    content = "\n".join(prompts) if isinstance(prompts, list) else prompts
    content = content.strip()

    if not content:
        print("No prompts generated. Skipping saving.")
        return None
    # Remove triple backtick wrappers if they exist.
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\n?", "", content)
        content = re.sub(r"\n?```$", "", content).strip()

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"Skipping invalid JSON: {e}")
        return None

    return parsed


def save_metadata(
    output_path: str, parsed: dict, image_prompt_info: dict, image_path: str
) -> None:
    """Save the generated metadata to the output JSONL file."""
    # Attach additional metadata to the parsed object
    parsed["domain"] = image_prompt_info["domain"]
    parsed["risk"] = image_prompt_info["risk"]
    parsed["image_path"] = image_path

    # Reorder the keys for consistency in the output file.
    parsed = {
        "domain": parsed["domain"],
        "risk": parsed["risk"],
        "image_prompt": parsed["image_prompt"],
        "image_path": parsed["image_path"],
        "metadata": parsed["metadata"],
    }

    with open(output_path, "a", encoding="utf-8") as f:
        json_line = json.dumps(parsed, ensure_ascii=False)
        f.write(json_line + "\n")
    print("Metadata saved successfully.")


def get_arguments() -> argparse.Namespace:
    """Parse and return command-line arguments."""
    parser = argparse.ArgumentParser(description="Generate metadata from image prompts")
    parser.add_argument(
        "--config_file", type=str, required=True, help="Path to the configuration file"
    )
    # parser.add_argument('--system_prompt_path',
    #                     type=str, required=True,
    #                     help='Path to the system prompt file') # Ignore for now
    parser.add_argument(
        "--prompt_variant",
        type=str,
        default="v1",
        help="Version of the system prompt to use",
    )
    parser.add_argument(
        "--image_prompt_file",
        type=str,
        required=True,
        help="Path to the file containing image prompts",
    )
    parser.add_argument(
        "--images_folder",
        type=str,
        default="hiring_images",
        help="Folder to save generated images",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="metadata_ground_truth",
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
    """Generate metadata from image prompts."""
    # Parse command-line arguments
    args = get_arguments()

    # Load configuration settings from file
    yaml_config = load_config(args.config_file)

    # Load image prompts from the specified JSONL file
    image_prompt_file = args.image_prompt_file
    if not os.path.exists(image_prompt_file):
        raise FileNotFoundError(f"Image prompt file {image_prompt_file} not found.")
    with open(image_prompt_file, "r", encoding="utf-8") as f:
        image_prompts = [json.loads(line) for line in f if line.strip()]
    if not image_prompts:
        raise ValueError(
            f"No valid image prompts found in {image_prompt_file}. Please ensure the file contains valid JSON lines."
        )

    # Use the first image prompt (this will be updated in the loop)
    image_prompt = image_prompts[0]["image_prompt"]

    # Retrieve OpenAI API key from environment variables
    api_key = config("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    # Set model parameters from configuration
    model = yaml_config["gpt"].get("model", "gpt-4o")  # Model choice
    batch_size = yaml_config["gpt"].get("batch_size", 5)  # Batch size for processing
    max_tokens = yaml_config["gpt"].get("max_tokens", 2048)  # Max tokens for response
    temperature = yaml_config["gpt"].get(
        "temperature", 0.7
    )  # Temperature for response variability
    print(
        f"Using model: {model}, batch size: {batch_size}, max tokens: {max_tokens}, temperature: {temperature}"
    )

    # Load system prompt used for generating metadata
    system_prompt = metadata_prompt[args.prompt_variant]
    print(f"Using system prompt:\n{system_prompt}")

    # Ensure the output directory exists
    output_dir = args.output_dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    domain = image_prompts[0].get("domain", "unknown")
    risk = image_prompts[0].get("risk", "unknown")

    # Checkpoint file to track progress in case of interruptions
    checkpoint_file = os.path.join(
        output_dir, f"checkpoint_metadata_{domain}_{risk}.txt"
    )
    last_processed_index = load_checkpoint(checkpoint_file)

    print(f"Total image prompts to process: {len(image_prompts)}")
    if last_processed_index >= len(image_prompts) - 1:
        print("All image prompts have already been processed. Exiting.")
        return

    # Loop through each image prompt and generate metadata
    for i in range(last_processed_index + 1, len(image_prompts)):
        image_prompt = image_prompts[i]["image_prompt"]
        image_path = os.path.join(
            args.images_folder, f"{domain}_{risk}_image_{i + 1}.png"
        )
        if not os.path.exists(image_path):
            print(
                f"Image file {image_path} does not exist. Skipping prompt generation for this image."
            )
            continue

        print(f"Processing image prompt {i + 1}/{len(image_prompts)}: {image_prompt}")

        parsed = process_image_prompt_metadata(
            image_prompt,
            system_prompt,
            api_key,
            model,
            batch_size,
            max_tokens,
            temperature,
        )

        if not parsed:
            continue  # Skip if no valid metadata was generated

        image_prompt_info = image_prompts[i]
        if not isinstance(image_prompt_info, dict):
            print(
                f"Invalid image prompt format for prompt {i + 1}. Expected a dictionary."
            )
            continue
        if "domain" not in image_prompt_info or "risk" not in image_prompt_info:
            print(f"Missing 'domain' or 'risk' in image prompt {i + 1}. Skipping.")
            continue

        save_metadata(
            os.path.join(output_dir, args.output_file),
            parsed,
            image_prompt_info,
            image_path,
        )

        save_checkpoint(checkpoint_file, i)


if __name__ == "__main__":
    main()


# To run:
# To run this script, use the following command from the terminal:
#
# uv run metadataGeneration.py --config_file <path_to_config_yaml> \
# --prompt_variant <prompt_version> \
# --image_prompts_file <path_to_image_prompts_jsonl> \
# --output_file <output_jsonl_file>
#
# Example:
# uv run metadata_generation.py --config_file ../../config.yaml \
# --prompt_variant v1 \
# --image_prompt_file prompts/hiring-representation_gaps.jsonl \
# --images_folder hiring_representation_gaps_images/ \
# --output_file hiring_representation_gaps.jsonl
