"""VQA Prompt Generation Script from Image Prompts."""

# Standard library imports
import argparse
import json
import os
import re
import sys

# Third-party imports
from pathlib import Path

from decouple import AutoConfig

# Import utility functions
from utils import (
    generate_prompts_vqa,
    load_checkpoint,
    load_config,
    save_checkpoint,
    save_vqa,
)


# Add local folder to path and import local modules
sys.path.append(os.path.dirname(__file__))
from system_prompt import vqa_prompts


PROJECT_ROOT = Path(__file__).resolve().parents[5]
config = AutoConfig(search_path=str(PROJECT_ROOT))


def process_image_prompt(
    image_prompt: str,
    system_prompt: str,
    image_path: str,
    api_key: str,
    model: str,
    batch_size: int,
    max_tokens: int,
    temperature: float,
) -> dict | None:
    """Generate metadata for a single image prompt."""
    prompts = generate_prompts_vqa(
        system_prompt,
        image_prompt,
        image_path,
        api_key,
        model,
        batch_size,
        max_tokens,
        temperature,
    )

    print(f"Generated prompts: {prompts}")

    # Prepare the content to write to the JSONL file.
    content = "\n".join(prompts) if isinstance(prompts, list) else prompts
    content = content.strip()

    if not content:
        print("No prompts generated. Skipping saving.")
        return None

    # Remove triple backtick code block wrappers if they exist.
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\n?", "", content)
        content = re.sub(r"\n?```$", "", content).strip()

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"Skipping invalid JSON: {e}")
        return None

    return parsed


def get_arguments() -> argparse.Namespace:
    """Parse and return command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate VQA prompts from image prompts"
    )
    parser.add_argument(
        "--config_file", type=str, required=True, help="Path to the configuration file"
    )
    # parser.add_argument('--system_prompt_path',
    #                     type=str, required=True,
    #                     help='Path to the system prompt file') # Ignore for now
    parser.add_argument(
        "--prompt_domain",
        type=str,
        default="risk",
        help="Top-level prompt family to use.",
    )
    parser.add_argument(
        "--prompt_variant",
        type=str,
        choices=["v1", "v2", "bias"],
        help="Variant of the prompt to use (e.g., v1, v2, bias).",
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
        default="vqa_ground_truth",
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
    """Generate VQA prompts from image prompts."""
    args = get_arguments()  # Parse command-line arguments.
    yaml_config = load_config(args.config_file)  # Load configuration settings.

    # Load image prompts from the specified JSONL file.
    image_prompt_file = args.image_prompt_file
    if not os.path.exists(image_prompt_file):
        raise FileNotFoundError(f"Image prompt file {image_prompt_file} not found.")
    with open(image_prompt_file, "r", encoding="utf-8") as f:
        image_prompts = [json.loads(line) for line in f if line.strip()]
    if not image_prompts:
        raise ValueError(
            f"No valid image prompts found in {image_prompt_file}. \
                         Please ensure the file contains valid JSON lines."
        )

    # Ensure the OpenAI API key is available.
    api_key = config("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    # Retrieve parameters for prompt generation from the config.
    model = yaml_config["gpt"].get("model", "gpt-4o")  # Model choice
    batch_size = yaml_config["gpt"].get("batch_size", 5)  # Batch size for processing
    max_tokens = yaml_config["gpt"].get("max_tokens", 2048)  # Max tokens for response
    temperature = yaml_config["gpt"].get(
        "temperature", 0.7
    )  # Temperature for response variability
    print(
        f"Using model: {model}, batch size: {batch_size}, max tokens: {max_tokens}, \
          temperature: {temperature}"
    )

    # Load the system prompt that will be used in generating the VQA prompts.
    system_prompt = vqa_prompts[args.prompt_domain][args.prompt_variant]
    print(f"Using system prompt:\n{system_prompt}")

    # Create the output directory if it does not exist.
    output_dir = args.output_dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get domain and risk from the first image prompt.
    domain = image_prompts[0].get("domain", "unknown")
    risk = image_prompts[0].get("risk", "unknown")

    # Initialize a checkpoint file to track progress.
    checkpoint_file = os.path.join(output_dir, f"checkpoint_vqa_{domain}_{risk}.txt")
    last_processed_index = load_checkpoint(checkpoint_file)

    print(f"Total image prompts to process: {len(image_prompts)}")
    if last_processed_index >= len(image_prompts) - 1:
        print("All image prompts have already been processed. Exiting.")
        return

    # Loop over each image prompt that hasn't been processed.
    for i in range(last_processed_index + 1, len(image_prompts)):
        image_prompt = image_prompts[i]["image_prompt"]
        image_path = os.path.join(
            args.images_folder, f"{domain}_{risk}_image_{i + 1}.png"
        )

        # Skip the image prompt if the corresponding image file does not exist.
        if not os.path.exists(image_path):
            print(
                f"Image file {image_path} does not exist. \
                  Skipping prompt generation for this image."
            )
            continue

        print(f"Processing image prompt {i + 1}/{len(image_prompts)}: {image_prompt}")

        # Generate prompts using the utility function.
        parsed = process_image_prompt(
            image_prompt,
            system_prompt,
            image_path,
            api_key,
            model,
            batch_size,
            max_tokens,
            temperature,
        )

        # Add domain, risk, metadata, and image details to the parsed JSON.
        image_prompt_info = image_prompts[i]
        if not isinstance(image_prompt_info, dict):
            print(
                f"Invalid image prompt format for prompt {i + 1}. Expected a dictionary."
            )
            continue
        if "domain" not in image_prompt_info or "risk" not in image_prompt_info:
            print(f"Missing 'domain' or 'risk' in image prompt {i + 1}. Skipping.")
            continue
        if parsed is None:
            # log and skip this item
            print("parse failed; skipping")  # or logger.warning(...)
            continue  # or return, depending on your loop/flow

        # Save the generated VQA prompts to the output JSONL file.
        save_vqa(
            os.path.join(output_dir, args.output_file),
            parsed,
            image_prompt_info,
            image_path,
            image_prompt,
        )

        # Save the current index to the checkpoint file.
        save_checkpoint(
            checkpoint_file, i
        )  # Save the current index to the checkpoint file.


if __name__ == "__main__":
    main()


# To run:
# To run this script, use the following command from the terminal:
#
# uv run vqa_generation.py --config_file <path_to_config_yaml> \
# --image_prompts_file <path_to_image_prompts_jsonl> \
# --images_folder <folder_with_images> \
# --prompt_domain <domain> \
# --prompt_variant <variant> \
# --output_file <output_jsonl_file>
#
# Example:
# uv run vqa_generation.py --config_file ../../config.yaml \
# --image_prompt_file prompts/hiring-representation_gaps.jsonl \
# --images_folder hiring_representation_gaps_images/ \
# --prompt_domain risk --prompt_variant v2 \
# --output_file hiring_representation_gaps.jsonl
