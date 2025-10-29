"""
Synthetic image dataset generation utilities.

Generates prompts, images, metadata, and VQA pairs across domain/risk dimensions.

Pipeline:
1. prompt_generation: Structured image prompt JSON objects via LLM.
2. image_generation: Synthetic images via Gemini API.
3. metadata_generation: Captions and annotations for each image prompt.
4. vqa_generation: Visual QA pairs conditioned on image and prompt.
5. csr_vqa_generation: Variant of VQA generation.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

import yaml
from decouple import AutoConfig
from metadata_generation import process_image_prompt_metadata, save_metadata

# Local utility functions for configuration and prompt generation
from utils import (
    generate_image_gemini,
    generate_prompts_with_userprompt,
    # generate_prompts_without_image,
    load_checkpoint,
    load_config,
    load_prompt,
    load_prompt_path,
    save_checkpoint,
    # generate_prompts_vqa,
    save_vqa,
)
from vqa_generation import process_image_prompt


# Ensure local modules are importable
sys.path.append(os.path.dirname(__file__))
from system_prompt import image_prompt_generation, metadata_prompt, vqa_prompts


PROJECT_ROOT = Path(__file__).resolve().parents[5]
config = AutoConfig(search_path=str(PROJECT_ROOT))


def prompt_generation(args: argparse.Namespace) -> None:
    """Generate prompts and save them to a file."""
    # Load configuration settings from the specified file
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


def image_generation(args: argparse.Namespace) -> None:
    """Generate synthetic images based on prompts and configuration."""
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


def metadata_generation(args: argparse.Namespace) -> None:  # noqa: PLR0915
    """Generate metadata from image prompts."""
    # Load configuration settings from file
    yaml_config = load_config(args.config_file)

    domain = args.domain
    risk = args.risk
    prompts = load_prompt_path(args.prompt_yaml)
    # Get the prompt path based on domain and risk.
    try:
        prompt_path = prompts["prompts"][domain][risk]
    except KeyError as e:
        raise KeyError(
            f"Prompt for domain '{domain}' and risk '{risk}' not found in {args.prompt_yaml}"
        ) from e

    print(
        f"\nGenerating image for domain: {domain}, risk: {risk} has prompt path:{prompt_path}"
    )

    # Load image prompts from the specified JSONL file
    image_prompt_file = prompt_path
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

    # Checkpoint file to track progress in case of interruptions
    checkpoint_file = os.path.join(
        output_dir, f"checkpoint_metadata_{domain}-{risk}.txt"
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
            args.images_folder, f"{domain}-{risk}_image_{i + 1}.png"
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


def vqa_generation(args: argparse.Namespace) -> None:
    """Generate VQA prompts from image prompts."""
    # Load configuration from the provided file
    yaml_config = load_config(args.config_file)
    domain = args.domain
    risk = args.risk

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

    # Initialize a checkpoint file to track progress.
    checkpoint_file = os.path.join(output_dir, f"checkpoint_vqa_{domain}-{risk}.txt")
    last_processed_index = load_checkpoint(checkpoint_file)

    print(f"Total image prompts to process: {len(image_prompts)}")
    if last_processed_index >= len(image_prompts) - 1:
        print("All image prompts have already been processed. Exiting.")
        return

    # Loop over each image prompt that hasn't been processed.
    for i in range(last_processed_index + 1, len(image_prompts)):
        image_prompt = image_prompts[i]["image_prompt"]
        image_path = os.path.join(
            args.images_folder, f"{domain}-{risk}_image_{i + 1}.png"
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


def csr_vqa_generation(args: argparse.Namespace) -> None:
    """Generate VQA prompts from image prompts."""
    # Load configuration from the provided file
    yaml_config = load_config(args.config_file)
    domain = args.domain
    risk = args.risk

    # Load image prompts from a jsonl file
    image_prompt_file = args.image_prompt_file
    if not os.path.exists(image_prompt_file):
        raise FileNotFoundError(f"Image prompt file {image_prompt_file} not found.")
    with open(image_prompt_file, "r", encoding="utf-8") as f:
        image_prompts = [json.loads(line) for line in f if line.strip()]
    if not image_prompts:
        raise ValueError(
            f"No valid image prompts found in {image_prompt_file}. Please ensure the file contains valid JSON lines."
        )

    # Validate that the OpenAI API key is set in the environment
    api_key = config("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    # Set model parameters from configuration
    model = yaml_config["gpt"].get("model", "gpt-4o")  # Model choice
    batch_size = yaml_config["gpt"].get("batch_size", 5)  # Batch size for API calls
    max_tokens = yaml_config["gpt"].get("max_tokens", 2048)  # Max tokens for response
    temperature = yaml_config["gpt"].get(
        "temperature", 0.7
    )  # Temperature for response randomness
    print(
        f"Using model: {model}, batch size: {batch_size}, max tokens: {max_tokens}, temperature: {temperature}"
    )

    # Load system prompt from the imported module
    system_prompt = vqa_prompts[args.prompt_domain][args.prompt_variant]

    # Create output directory if it doesn't exist
    output_dir = args.output_dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    print(f"Output directory created: {output_dir}")

    # Initialize checkpoint to resume progress if available
    checkpoint_file = os.path.join(
        output_dir, f"checkpoint_csr_vqa_{domain}-{risk}.txt"
    )
    last_processed_index = load_checkpoint(checkpoint_file)

    print(f"Total image prompts to process: {len(image_prompts)}")
    if last_processed_index >= len(image_prompts) - 1:
        print("All image prompts have already been processed. Exiting.")
        return

    # Process each image prompt starting from the index after the last checkpoint
    for i in range(last_processed_index + 1, len(image_prompts)):
        image_prompt = image_prompts[i]["image_prompt"]
        image_path = image_prompts[i]["image_path"]
        # image_path = os.path.join(
        #     args.images_folder, f"{domain}-{risk}_image_{i + 1}.png"
        # )

        # Skip if the image file does not exist
        if not os.path.exists(image_path):
            print(
                f"Image file {image_path} does not exist. Skipping prompt generation for this image."
            )
            continue

        print(f"Processing image prompt {i + 1}/{len(image_prompts)}: {image_prompt}")

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

        # Add additional information from the image prompt to the parsed result
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

        # Save the csr-vqa prompts to the output JSONL file
        save_vqa(
            os.path.join(output_dir, args.output_file),
            parsed,
            image_prompt_info,
            image_path,
            image_prompt,
        )

        # Save the checkpoint after processing each prompt
        save_checkpoint(checkpoint_file, i)
