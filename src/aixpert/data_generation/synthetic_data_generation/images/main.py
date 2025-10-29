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
from typing import Any, Protocol

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


class Subparsers(Protocol):
    """Protocol for argparse subparsers."""

    def add_parser(self, name: str, **kwargs: Any) -> argparse.ArgumentParser:
        """Create, register, and return a new argparse.ArgumentParser instance."""
        ...


def base_parser() -> argparse.ArgumentParser:
    """Create the base argument parser."""
    return argparse.ArgumentParser(
        description="Synthetic Image Data Generation with VQA"
    )


def add_prompt_generation(subparsers: Subparsers) -> None:
    """Stage 1: Prompt Generation."""
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
        "--output_dir",
        type=str,
        default="prompts",
        help="Directory to save output files",
    )
    stage1_parser.add_argument(
        "--output_file",
        type=str,
        default="prompts.jsonl",
        help="File to save generated prompts",
    )


def add_image_generation(subparsers: Subparsers) -> None:
    """Stage 2: Image Generation."""
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


def add_metadata_generation(subparsers: Subparsers) -> None:
    """Stage 3: Metadata Generation."""
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
        "--domain",
        type=str,
        choices=["hiring", "legal", "healthcare"],
        required=True,
        help="Domain for which to generate metadata",
    )
    stage3_parser.add_argument(
        "--risk",
        required=True,
        choices=["bias", "toxicity", "representation_gaps", "security_risks"],
        help="Risk type for the metadata generation",
    )
    stage3_parser.add_argument(
        "--prompt_yaml", type=str, required=True, help="Path to the prompt YAML file"
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


def add_csr_vqa_generation(subparsers: Subparsers) -> None:
    """Stage 4a: CSR VQA Generation."""
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
        "--domain",
        type=str,
        choices=["hiring", "legal", "healthcare"],
        required=True,
        help="Domain for which to generate VQA prompts",
    )
    stage4a_parser.add_argument(
        "--risk",
        required=True,
        choices=["bias", "toxicity", "representation_gaps", "security_risks"],
        help="Risk type for the VQA generation",
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


def add_vqa_generation(subparsers: Subparsers) -> None:
    """Stage 4b: VQA Generation."""
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
        "--domain",
        type=str,
        choices=["hiring", "legal", "healthcare"],
        required=True,
        help="Domain for which to generate VQA prompts",
    )
    stage4b_parser.add_argument(
        "--risk",
        required=True,
        choices=["bias", "toxicity", "representation_gaps", "security_risks"],
        help="Risk type for the VQA generation",
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


def all_stages_parser(subparsers: Subparsers) -> None:
    """Parser for running all stages sequentially."""
    all_stages = subparsers.add_parser("all_stages", help="Run all stages sequentially")
    all_stages.add_argument("--config_file", type=str, required=True)
    all_stages.add_argument("--prompt_yaml", type=str, required=True)
    all_stages.add_argument(
        "--domain", type=str, choices=["hiring", "legal", "healthcare"], required=True
    )
    all_stages.add_argument(
        "--risk",
        choices=["bias", "toxicity", "representation_gaps", "security_risks"],
        required=True,
    )

    # allow overrides or use sensible defaults
    all_stages.add_argument("--images_folder", type=str, default=None)
    all_stages.add_argument(
        "--metadata_output_dir", type=str, default="metadata_ground_truth"
    )
    all_stages.add_argument("--metadata_output_file", type=str, default=None)
    all_stages.add_argument("--vqa_output_dir", type=str, default="vqa_ground_truth")
    all_stages.add_argument("--vqa_output_file", type=str, default=None)


def get_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = base_parser()

    subparsers = parser.add_subparsers(
        dest="stage", help="Stages to run", required=True
    )

    add_prompt_generation(subparsers)
    add_image_generation(subparsers)
    add_metadata_generation(subparsers)
    add_csr_vqa_generation(subparsers)
    add_vqa_generation(subparsers)
    all_stages_parser(subparsers)

    return parser.parse_args()


def run_all_stages(args: argparse.Namespace) -> None:
    """Run all stages sequentially."""
    print("Running all stages...")

    # Derive filenames if not supplied
    stem = f"{args.domain}-{args.risk}"
    images_folder = args.images_folder or f"{stem}_images"
    metadata_file = args.metadata_output_file or f"{stem}_metadata.jsonl"
    vqa_file = args.vqa_output_file or f"{stem}_vqa.jsonl"
    image_prompt_file = os.path.join(args.metadata_output_dir, metadata_file)

    # 1) Prompt generation
    print("\n--- Stage 1: Prompt Generation ---")
    pg = argparse.Namespace(
        stage="prompt_generation",
        config_file=args.config_file,
        prompt_yaml=args.prompt_yaml,
        domain=args.domain,
        risk=args.risk,
        output_dir="prompts",
        output_file=f"{stem}.jsonl",
    )
    prompt_generation(pg)

    # 2) Image generation
    print("\n--- Stage 2: Image Generation ---")
    ig = argparse.Namespace(
        stage="image_generation",
        config_file=args.config_file,
        prompt_yaml=args.prompt_yaml,
        domain=args.domain,
        risk=args.risk,
    )
    image_generation(ig)

    # 3) Metadata generation
    print("\n--- Stage 3: Metadata Generation ---")
    mg = argparse.Namespace(
        stage="metadata_generation",
        config_file=args.config_file,
        prompt_variant="v1",
        domain=args.domain,
        risk=args.risk,
        prompt_yaml=args.prompt_yaml,
        images_folder=images_folder,
        output_dir=args.metadata_output_dir,
        output_file=metadata_file,
    )
    metadata_generation(mg)

    # 4) VQA generation (risk VQA)
    print("\n--- Stage 4a: VQA Generation ---")
    vg = argparse.Namespace(
        stage="vqa_generation",
        config_file=args.config_file,
        prompt_domain="risk",
        prompt_variant="v1",
        domain=args.domain,
        risk=args.risk,
        image_prompt_file=image_prompt_file,
        images_folder=images_folder,
        output_dir=args.vqa_output_dir,
        output_file=vqa_file,
    )
    vqa_generation(vg)

    # 5) CSR-VQA generation
    print("\n--- Stage 4b: CSR-VQA Generation ---")
    csg = argparse.Namespace(
        stage="csr-vqa_generation",
        config_file=args.config_file,
        prompt_domain="csr",
        prompt_variant="simple",
        domain=args.domain,
        risk=args.risk,
        image_prompt_file=image_prompt_file,
        images_folder=images_folder,
        output_dir="vqa_commonsense_ground_truth",
        output_file=f"{stem}_csr_vqa.jsonl",
    )
    csr_vqa_generation(csg)

    print("\nAll stages completed successfully.")


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
