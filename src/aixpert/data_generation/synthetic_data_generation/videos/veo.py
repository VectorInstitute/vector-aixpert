"""Video generation using Veo from Google Gemini."""

import argparse
import os
from pathlib import Path

from decouple import AutoConfig

# from dotenv import load_dotenv
from utils import (
    build_checkpoint_path,
    generate_video_veo,
    load_checkpoint,
    load_config,
    load_prompt,
    save_checkpoint,
    save_videos,
)


PROJECT_ROOT = Path(__file__).resolve().parents[5]
config = AutoConfig(search_path=str(PROJECT_ROOT))


def get_arguments() -> argparse.Namespace:
    """Parse command line arguments for configuration and prompt details."""
    parser = argparse.ArgumentParser(description="Generate synthetic data")
    parser.add_argument(
        "--config_file", type=str, required=True, help="Path to the configuration file"
    )
    parser.add_argument(
        "--domain", type=str, required=True, help="Domain for video generation"
    )
    parser.add_argument(
        "--risk", type=str, required=True, help="Risk type for video generation"
    )
    parser.add_argument(
        "--prompt_yaml", type=str, required=True, help="Path to the prompt YAML file"
    )
    parser.add_argument(
        "--num_videos",
        type=int,
        default=1,
        help="Number of videos to generate per prompt",
    )
    parser.add_argument(
        "--model_family",
        type=str,
        default="veo",
        help="Model family to use for generation (default: veo)",
    )
    return parser.parse_args()


def process_prompts(
    *,
    veo_params: dict,
    number_of_videos: int,
    prompts: list,
    domain: str,
    risk: str,
    checkpoint_file: str,
) -> None:
    """Process and generate videos for the given prompts."""
    # Determine where to start (resume if checkpoint exists).
    last_processed_index, _ = load_checkpoint(checkpoint_file)
    start_index = last_processed_index + 1
    if start_index >= len(prompts):
        print(
            f"All prompts have already been processed (start_index: {start_index} >= total prompts: {len(prompts)}). Exiting."
        )
        return

    # Create folder if it doesn't exist.
    folder_name = f"{domain}_{risk}_videos"
    os.makedirs(folder_name, exist_ok=True)
    print(f"Output folder: {folder_name}")

    # Process prompts from start_index to end.
    for i in range(start_index, len(prompts)):
        prompt = prompts[i]
        print(f"\n==== Prompt {i + 1} / {len(prompts)} ====")
        print(f"video_prompt: {prompt.get('video_prompt')}\n")

        # Skip if all prior run videos for this prompt already exist.
        all_videos_exist = True
        for n in range(1, number_of_videos + 1):  # Check for all expected video files
            expected_video_filename = f"{domain}_{risk}_video_{i + 1}_{n}.mp4"
            expected_video_path = os.path.join(folder_name, expected_video_filename)
            if not os.path.exists(expected_video_path):
                all_videos_exist = False
                break

        if all_videos_exist:
            print(f"All videos for prompt {i + 1} already exist. Skipping generation.")
            save_checkpoint(checkpoint_file, i)
            continue
        try:
            client, videos = generate_video_veo(
                veo_params=veo_params,
                prompt=prompt["video_prompt"],
                negative_prompt=None,
            )
            print("Video generation successful.")
            print(f"Number of videos generated: {len(videos)}")

            # Save all videos and update checkpoint.
            save_videos(
                client=client,
                videos=videos,
                folder_name=folder_name,
                domain=domain,
                risk=risk,
                index=i,
                checkpoint_file=checkpoint_file,
            )

        except Exception as e:
            print(f"Error generating or saving video: {e}")


def main() -> None:
    """Generate synthetic videos based on prompts and configuration."""
    args = get_arguments()

    # Load configuration and prompt paths.
    yaml_config = load_config(args.config_file)
    domain = args.domain
    risk = args.risk

    print(f"\nGenerating videos for domain: {domain}, risk: {risk}")

    # Ensure the API key is available from environment variables.
    api_key = config("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
    print("Using GEMINI_API_KEY from environment variables.")

    # Retrieve GEMINI configuration options.
    config_name = args.model_family  # e.g., "veo"
    model = yaml_config[config_name].get("model")  # Model choice
    aspect_ratio = yaml_config[config_name].get("aspectRatio")  # Aspect ratio
    person_generation = yaml_config[config_name].get(
        "personGeneration"
    )  # Person generation setting

    print(
        f"Using model: {model} with aspect ratio: {aspect_ratio}, person generation: {person_generation}"
    )

    # Build checkpoint path automatically.
    checkpoint_file = build_checkpoint_path(domain, risk)
    print(f"Checkpoint file: {checkpoint_file}")

    # Load the actual prompt using the prompt path.
    prompts = load_prompt(args.prompt_yaml, domain, risk)
    if not prompts:
        raise ValueError(
            f"No prompts found for domain '{domain}' and risk '{risk}' in {args.prompt_yaml}"
        )

    print(f"Total prompts loaded: {len(prompts)}")

    # Make a veo_params dictionary to hold veo-specific parameters.
    veo_params = {
        "api_key": api_key,
        "model_name": model,
        "aspect_ratio": aspect_ratio,
        "person_generation": person_generation,
        "number_of_videos": args.num_videos,
        "duration_seconds": 8,
    }
    # Process and generate videos for the loaded prompts.
    process_prompts(
        veo_params=veo_params,
        number_of_videos=args.num_videos,
        prompts=prompts,
        domain=domain,
        risk=risk,
        checkpoint_file=checkpoint_file,
    )


if __name__ == "__main__":
    main()


# To run this script, use the following command:
# python veo.py --config_file path/to/config.yaml \
# --prompt_yaml path/to/prompt.yaml --domain hiring --risk bias

# For example:
# python3 veo.py --config_file ../../config.yaml  \
# --prompt_yaml prompt_paths.yaml --domain hiring --risk bias
