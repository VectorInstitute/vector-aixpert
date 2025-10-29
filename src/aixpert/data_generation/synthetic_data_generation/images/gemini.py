"""Image generation using Gemini API."""

import argparse
import os
from pathlib import Path

from decouple import AutoConfig

# OpenAI packages
from utils import generate_image_gemini, load_config, load_prompt, load_prompt_path


PROJECT_ROOT = Path(__file__).resolve().parents[5]
config = AutoConfig(search_path=str(PROJECT_ROOT))


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
        "--risk",
        required=True,
        choices=["bias", "toxicity", "representation_gaps", "security_risks"],
        help="Risk type for the image generation",
    )
    return parser.parse_args()


def main() -> None:
    """Generate synthetic images based on prompts and configuration."""
    args = get_arguments()

    # Load configuration and prompt paths.
    yaml_config = load_config(args.config_file)
    prompts = load_prompt_path(args.prompt_yaml)

    # Ensure the OpenAI API key is available from environment variables.
    api_key = config("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
    print("Using GEMINI_API_KEY from environment variables.")

    # Retrieve GEMINI configuration options.
    model = yaml_config["gemini"].get(
        "model", "imagen-4.0-generate-001"
    )  # Model choice
    number_of_images = yaml_config["gemini"].get(
        "numberOfImages", 1
    )  # Number of images to generate per prompt
    img_size = yaml_config["gemini"].get("sampleImageSize", "1024x1024")  # Image size
    aspect_ratio = yaml_config["gemini"].get("aspectRatio", "1:1")  # Aspect ratio
    person_generation = yaml_config["gemini"].get(
        "personGeneration", "ALLOW_ALL"
    )  # Person generation setting

    print(
        f"Using model: {model} with quality: {img_size}, aspect ratio: {aspect_ratio}, person generation: {person_generation}"
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
            # api_key, model_name, prompt, img_size, aspect_ratio,
            # number_of_images, person_generation
            image = generate_image_gemini(
                api_key=api_key,
                model_name=model,
                prompt=prompt["image_prompt"],
                img_size=img_size,
                aspect_ratio=aspect_ratio,
                number_of_images=number_of_images,
                person_generation=person_generation,
            )
            print("Image generated successfully.")

            # Create folder if it doesn't exist.
            folder_name = f"{domain}-{risk}_images"
            os.makedirs(folder_name, exist_ok=True)
            print(f"Saving image to folder: {folder_name}")

            # Define the output filename and save the image.
            output_filename = f"{domain}-{risk}_image_{i + 1}.png"
            output_filename = os.path.join(folder_name, output_filename)

            with open(output_filename, "wb") as img_file:
                img_file.write(image)
            print(f"Image saved as {output_filename}")

        except Exception as e:
            print(f"Error generating or saving image: {e}")

        # break # Remove this break if you want to generate images for all prompts


if __name__ == "__main__":
    main()
