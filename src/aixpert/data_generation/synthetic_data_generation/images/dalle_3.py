"""Image generation using DALL-E 3 from OpenAI."""

import argparse

# OpenAI packages
import os

from dotenv import load_dotenv
from utils import generate_image_openai, load_config, load_prompt, load_prompt_path


def get_arguments() -> argparse.Namespace:
    """Parse command line arguments for configuration and prompt details."""
    parser = argparse.ArgumentParser(
        description="Generate synthetic images using DALL-E 3."
    )
    parser.add_argument(
        "--config_file", type=str, required=True, help="Path to the configuration file"
    )
    parser.add_argument(
        "--prompt_yaml", type=str, required=True, help="Path to the prompt YAML file"
    )
    parser.add_argument(
        "--domain",
        choices=["hiring", "legal", "healthcare", "coding", "social_media"],
        required=True,
        help="Domain for the image generation",
    )
    parser.add_argument(
        "--risk", required=True, help="Risk type for the image generation"
    )
    return parser.parse_args()


def main() -> None:
    """Generate images based on prompts and configuration."""
    args = get_arguments()

    # Load configuration and prompt paths.
    config = load_config(args.config_file)
    prompts = load_prompt_path(args.prompt_yaml)
    load_dotenv()

    # Ensure the OpenAI API key is available from environment variables.
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    print("Using OpenAI API Key from environment variable.")

    # Retrieve DALL-E configuration options.
    model = config["dalle_config"].get("model", "dall-e-3")  # Model choice
    quality = config["dalle_config"].get("quality", "standard")  # Quality setting
    style = config["dalle_config"].get("style", "vivid")  # Style setting
    img_size = config["dalle_config"].get("img_size", "1024x1024")  # Image size

    print(
        f"Using model: {model} with quality: {quality}, style: {style}, image size: {img_size}"
    )

    domain = args.domain
    risk = args.risk

    # Get the prompt path based on domain and risk.
    try:
        prompt_path = prompts["prompts"][domain][risk]
    except KeyError as e:
        raise KeyError(
            f"Prompt for domain '{domain}' and risk '{risk}' not found in {args.prompt_yaml}"
        ) from e

    print(f"\nGenerating image for domain: {domain}, risk: {risk}")
    print(f"\nPrompt:\n{prompt_path}")

    # Load the actual prompt using the prompt path.
    prompts = load_prompt(prompt_path, domain, risk)
    if not prompts:
        raise ValueError(
            f"No prompts found for domain '{domain}' and risk '{risk}' in {args.prompt_yaml}"
        )

    # Generate and save images for each prompt.
    for i in range(len(prompts)):
        prompt = prompts[i]
        try:
            print(f"Generating image with prompt: {prompt['image_prompt']}")
            image = generate_image_openai(
                api_key, model, prompt["image_prompt"], style, img_size
            )

            # Create folder if it doesn't exist.
            folder_name = f"{domain}_{risk}_images"
            os.makedirs(folder_name, exist_ok=True)
            print(f"Saving image to folder: {folder_name}")

            # Define the output filename and save the image.
            output_filename = f"{domain}_{risk}_image_{i + 1}.png"
            output_filename = os.path.join(folder_name, output_filename)

            with open(output_filename, "wb") as img_file:
                img_file.write(image)
            print(f"Image saved as {output_filename}")

        except Exception as e:
            print(f"Error generating or saving image: {e}")

        # break # Remove this break if you want to generate images for all prompts


if __name__ == "__main__":
    main()


# To run this script, use the following command:
# python dalle_3.py --config_file path/to/config.yaml \
# --prompt_yaml path/to/prompt.yaml --domain hiring --risk bias

# For example
# python3 dalle_3.py --config_file ../../config.yaml  \
# --prompt_yaml prompt_paths.yaml --domain hiring --risk bias
