"""
Main script to generate synthetic image data.

Generates image prompts, images, metadata, and VQA/CSR-VQA prompts across
configurable domains and risk types.
"""

# Standard library imports
import argparse
import os
import sys
from pathlib import Path

from decouple import AutoConfig
from system_utils import (
    csr_vqa_generation,
    image_generation,
    metadata_generation,
    prompt_generation,
    vqa_generation,
)


# Ensure local modules are importable
sys.path.append(os.path.dirname(__file__))

PROJECT_ROOT = Path(__file__).resolve().parents[5]
config = AutoConfig(search_path=str(PROJECT_ROOT))


def get_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate prompts for synthetic images using GPT-4o."
    )

    subparsers = parser.add_subparsers(
        dest="stage", help="Stages to run", required=True
    )

    # Stage 1: Prompt Generation
    stage1_parser = subparsers.add_parser(
        "prompt_generation", help="Generate prompts for synthetic images"
    )
    stage1_parser.add_argument(
        "--config_file", type=str, required=True, help="Path to the configuration file"
    )
    stage1_parser.add_argument(
        "--prompt_yaml", type=str, required=True, help="Path to the prompt YAML file"
    )
    stage1_parser.add_argument(
        "--domain",
        type=str,
        choices=["hiring", "legal", "healthcare"],
        required=True,
        help="Domain for which to generate prompts",
    )
    stage1_parser.add_argument(
        "--risk",
        type=str,
        required=True,
        help="Risk category for the prompts (e.g., bias_v1, toxicity etc. \
            based on the system prompt file)",
    )
    stage1_parser.add_argument(
        "--output_file",
        type=str,
        default="prompts.jsonl",
        help="File to save generated prompts",
    )

    # Stage 2: Image Generation
    stage2_parser = subparsers.add_parser(
        "image_generation", help="Generate synthetic images based on prompts"
    )
    stage2_parser.add_argument(
        "--config_file", type=str, required=True, help="Path to the configuration file"
    )
    stage2_parser.add_argument(
        "--prompt_yaml", type=str, required=True, help="Path to the prompt YAML file"
    )
    stage2_parser.add_argument(
        "--domain",
        type=str,
        choices=["hiring", "legal", "healthcare"],
        required=True,
        help="Domain for which to generate prompts",
    )
    stage2_parser.add_argument(
        "--risk",
        required=True,
        choices=["bias", "toxicity", "representation_gaps", "security_risks"],
        help="Risk type for the image generation",
    )

    # Stage 3: Metadata Generation
    stage3_parser = subparsers.add_parser(
        "metadata_generation", help="Generate metadata from image prompts"
    )
    stage3_parser.add_argument(
        "--config_file", type=str, required=True, help="Path to the configuration file"
    )
    stage3_parser.add_argument(
        "--prompt_variant",
        type=str,
        default="v1",
        help="Version of the system prompt to use",
    )
    stage3_parser.add_argument(
        "--image_prompt_file",
        type=str,
        required=True,
        help="Path to the file containing image prompts",
    )
    stage3_parser.add_argument(
        "--images_folder",
        type=str,
        default="hiring_images",
        help="Folder to save generated images",
    )
    stage3_parser.add_argument(
        "--output_dir",
        type=str,
        default="metadata_ground_truth",
        help="Directory to save output files",
    )
    stage3_parser.add_argument(
        "--output_file",
        type=str,
        default="prompts_metadata.jsonl",
        help="File to save generated prompts",
    )

    # Stage 4a: csr-VQA Generation
    stage4a_parser = subparsers.add_parser(
        "csr-vqa_generation", help="Generate CSR VQA prompts from image prompts"
    )
    stage4a_parser.add_argument(
        "--config_file", type=str, required=True, help="Path to the configuration file"
    )
    stage4a_parser.add_argument(
        "--prompt_domain",
        type=str,
        default="csr",
        help="Top-level prompt family to use.",
    )
    stage4a_parser.add_argument(
        "--prompt_variant",
        type=str,
        choices=["v1", "simple", "physical"],
        default="simple",
        help="Variant of the prompt to use (e.g., v1)",
    )
    stage4a_parser.add_argument(
        "--image_prompt_file",
        type=str,
        required=True,
        help="Path to the file containing image prompts",
    )
    stage4a_parser.add_argument(
        "--images_folder",
        type=str,
        default="hiring_images",
        help="Folder to save generated images",
    )
    stage4a_parser.add_argument(
        "--output_dir",
        type=str,
        default="vqa_commonsense_ground_truth",
        help="Directory to save output files",
    )
    stage4a_parser.add_argument(
        "--output_file",
        type=str,
        default="vqa_commonsense_prompts.jsonl",
        help="File to save generated prompts",
    )

    # Stage 4b: VQA Generation
    stage4b_parser = subparsers.add_parser(
        "vqa_generation", help="Generate VQA prompts from image prompts"
    )
    stage4b_parser.add_argument(
        "--config_file", type=str, required=True, help="Path to the configuration file"
    )
    stage4b_parser.add_argument(
        "--prompt_domain",
        type=str,
        default="risk",
        help="Top-level prompt family to use.",
    )
    stage4b_parser.add_argument(
        "--prompt_variant",
        type=str,
        choices=["v1", "v2", "bias"],
        help="Variant of the prompt to use (e.g., v1, v2, bias).",
    )
    stage4b_parser.add_argument(
        "--image_prompt_file",
        type=str,
        required=True,
        help="Path to the file containing image prompts",
    )
    stage4b_parser.add_argument(
        "--images_folder",
        type=str,
        default="hiring_images",
        help="Folder to save generated images",
    )
    stage4b_parser.add_argument(
        "--output_dir",
        type=str,
        default="vqa_ground_truth",
        help="Directory to save output files",
    )
    stage4b_parser.add_argument(
        "--output_file",
        type=str,
        default="prompts.jsonl",
        help="File to save generated prompts",
    )

    # Common arguments for all stages
    all_stages_parser = subparsers.add_parser("all_stages", help="Run all sequentially")
    all_stages_parser.add_argument(
        "--prompt_yaml", type=str, required=True, help="Path to the prompt YAML file"
    )
    all_stages_parser.add_argument(
        "--domain",
        type=str,
        choices=["hiring", "legal", "healthcare"],
        required=True,
        help="Domain for which to generate prompts",
    )
    all_stages_parser.add_argument(
        "--image_prompt_file",
        type=str,
        required=True,
        help="Path to the file containing image prompts",
    )

    return parser.parse_args()


def run_all_stages(args: argparse.Namespace) -> None:
    """Run all stages sequentially."""
    print("Running all stages...")

    # Stage 1: Prompt Generation
    print("\n--- Stage 1: Prompt Generation ---")
    prompt_generation(args)

    # Stage 2: Image Generation
    print("\n--- Stage 2: Image Generation ---")
    image_generation(args)

    # Stage 3: Metadata Generation
    print("\n--- Stage 3: Metadata Generation ---")
    metadata_generation(args)

    # Stage 4: VQA Generation
    print("\n--- Stage 4: VQA Generation ---")
    vqa_generation(args)

    print("\nAll stages completed successfully!")


def main(args: argparse.Namespace) -> None:
    """Run the selected stage."""
    if args.stage == "prompt_generation":
        prompt_generation(args)
    elif args.stage == "image_generation":
        image_generation(args)
    elif args.stage == "metadata_generation":
        metadata_generation(args)
    elif args.stage == "vqa_generation":
        vqa_generation(args)
    elif args.stage == "csr-vqa_generation":
        csr_vqa_generation(args)
    elif args.stage == "all_stages":
        run_all_stages(args)
    else:
        raise ValueError("Invalid stage selected. Use --help for available options.")


if __name__ == "__main__":
    args = get_arguments()
    print("Arguments received:", args)

    main(args)


# To run stage1:
# uv run main.py prompt_generation --config_file ../../config.yaml \
# --prompt_yaml prompt_paths.yaml --domain hiring --risk toxicity \
# --output_file test_stage1.jsonl

# To run stage2:
# uv run main.py image_generation --config_file ../../config.yaml \
# --prompt_yaml prompt_paths.yaml --domain hiring --risk toxicity

# To run stage3:
# uv run main.py metadata_generation --config_file ../../config.yaml \
# --prompt_variant v1 --image_prompt_file test_stage1.jsonl \
# --images_folder hiring_toxicity_images/ --output_dir meta_test/

# To run stage4a:
# uv run main.py vqa_generation --config_file ../../config.yaml \
# --prompt_domain risk --prompt_variant v1 \
# --image_prompt_file meta_test/prompts_metadata.jsonl \
# --images_folder hiring_toxicity_images/ --output_dir meta_test/ \
# --output_file test_vqa.jsonl

# To run stage4b:
# uv run main.py csr-vqa_generation --config_file ../../config.yaml \
# --prompt_domain csr --prompt_variant v1 \
# --image_prompt_file meta_test/prompts_metadata.jsonl \
# --images_folder hiring_toxicity_images/ \
# --output_dir meta_test/ --output_file test_csr_vqa.jsonl
