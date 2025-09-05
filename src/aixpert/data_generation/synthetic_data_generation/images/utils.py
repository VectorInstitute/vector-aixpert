"""Utility functions for image generation and prompt handling."""

# Standard libraries
import base64
import io
import json
import os
from contextlib import suppress

import requests
import yaml
from google import genai
from google.genai import types
from openai import OpenAI
from PIL import Image


def load_config(config_path: str) -> dict:
    """Load configuration from a YAML file."""
    try:
        with open(config_path, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Configuration file {config_path} not found.") from e
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML file {config_path}: {e}") from e


def load_prompt_path(prompt_yaml_path: str) -> dict:
    """Load prompt path from a YAML file."""
    try:
        with open(prompt_yaml_path, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Prompt YAML file {prompt_yaml_path} not found."
        ) from e
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML file {prompt_yaml_path}: {e}") from e


def load_prompt(prompt_path: str, domain: str, risk: str) -> list:
    """Load prompts from a JSONL file based on domain and risk."""
    # Prompt_path is a jsonl file where each line is a JSON object
    # that has domain, risk, and image_prompt keys.
    matching_prompts = []

    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    prompt = json.loads(line)
                    if prompt.get("domain") == domain and prompt.get("risk") == risk:
                        matching_prompts.append(prompt)
                except json.JSONDecodeError as e:
                    print(f"Skipping malformed JSON line: {e}")
    except FileNotFoundError:
        print(f"File not found: {prompt_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return matching_prompts


# Load checkpoint from a file
def load_checkpoint(checkpoint_file: str) -> int:
    """
    Load the last processed index from a checkpoint file.

    This allows resuming from the last processed prompt in case of interruptions.
    """
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, "r") as f:
            last_processed_index = int(f.read().strip())
        print(f"Resuming from index {last_processed_index + 1}")
        return last_processed_index
    print("No checkpoint found. Starting from the beginning.")
    return -1  # Start from the first prompt


# Save checkpoint to a file
def save_checkpoint(checkpoint_file: str, last_processed_index: int) -> None:
    """
    Save the current processing index to a checkpoint file.

    This allows resuming from the last processed prompt in case of interruptions.
    """
    with open(checkpoint_file, "w") as f:
        f.write(str(last_processed_index))
    print(f"Checkpoint saved at index {last_processed_index}.")


def generate_image_openai(
    api_key: str, model_name: str, prompt: str, style: str, img_size: str
) -> bytes:
    """Generate an image using OpenAI's image generation API."""
    client = OpenAI()
    client.api_key = api_key

    response = None  # Initialize response to None
    try:
        response = client.images.generate(
            model=model_name,
            prompt=prompt,
            style=style,  # Comment if using gpt-image-1
            size=img_size,
            n=1,
        )

        image_data = response.data[0]
        if image_data.b64_json:
            image_bytes = base64.b64decode(image_data.b64_json)
        elif image_data.url:
            print(f"Downloading image from URL: {image_data.url}")
            image_response = requests.get(image_data.url)
            image_response.raise_for_status()
            image_bytes = image_response.content
        else:
            raise ValueError("No image data returned (neither b64_json nor URL).")

        print("Image generated successfully.")
        return image_bytes

    except Exception as e:
        print(f"Error generating image: {e}")
        if response and hasattr(response, "data"):
            with suppress(Exception):
                print(f"Full response:\n{response}")
        raise


def generate_image_gemini(
    api_key: str,
    model_name: str,
    prompt: str,
    img_size: str,
    aspect_ratio: str,
    number_of_images: int,
    person_generation: str,
) -> bytes:
    """Generate an image using Gemini's image generation API."""
    client = genai.Client()
    client.api_key = api_key

    response = None  # Initialize response to None
    try:
        # print(types.GenerateImagesConfig.schema_json())
        # Print the configuration for debugging
        print(
            f"Generating image with model: {model_name}, prompt: {prompt}, size: {img_size}, aspect ratio: {aspect_ratio}, number of images: {number_of_images}, person generation: {person_generation}"
        )
        response = client.models.generate_images(
            model=model_name,
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=number_of_images,
                image_size=img_size,  # "1K" or "2K"
                aspect_ratio=aspect_ratio,  # "1:1","3:4","4:3","9:16","16:9"
                # person_generation=person_generation,
                # # "ALLOW_ALL" | "ALLOW_ADULT" | "DONT_ALLOW"
                # safety_filter_level="BLOCK_ONLY_HIGH",
                # # optional; omit to use defaults
            ),
        )

        # The SDK returns a PIL Image at .image
        return response.generated_images[0].image.image_bytes

    except Exception as e:
        print(f"Error generating image: {e}")
        if response is not None:
            with suppress(Exception):
                print(f"Full response:\n{response}")
        raise


def generate_prompts_without_image(
    system_prompt: str,
    image_prompt: str,
    api_key: str,
    model: str,
    batch_size: int,
    max_tokens: int,
    temperature: float,
) -> list | str | None:
    """Generate prompts using OpenAI's chat completion API without an image."""
    client = OpenAI()
    client.api_key = api_key

    try:
        user_message = (
            f"Image Prompt: {image_prompt}\n"
            "Follow the guidelines in the system prompt and generate output in the JSON format."
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            # n=batch_size
        )

        prompts = [
            choice.message.content.strip()
            for choice in response.choices
            if hasattr(choice, "message") and choice.message and choice.message.content
        ]
        return prompts if len(prompts) > 1 else prompts[0]
    except Exception as e:
        print(f"Error generating prompts: {e}")
        return None


# Used for making prompts for image generation
def generate_prompts_with_userprompt(
    system_prompt: str,
    api_key: str,
    model: str,
    batch_size: int,
    max_tokens: int,
    temperature: float,
) -> list | str | None:
    """Generate prompts using OpenAI's chat completion API with a user prompt."""
    client = OpenAI()
    client.api_key = api_key

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": "Generate 40 such examples that follow the guidelines in the system prompt and match the provided JSON output example.",
                },  # The user prompt is simplistic in nature here as the system prompt is already detailed
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            # n=batch_size
        )
        # Process responses: return a list if multiple responses are generated,
        # otherwise return a single prompt as a string.
        prompts = [
            choice.message.content.strip()
            for choice in response.choices
            if hasattr(choice, "message") and choice.message and choice.message.content
        ]
        return prompts if len(prompts) > 1 else prompts[0]
    except Exception as e:
        print(f"Error generating prompts: {e}")
        return None


def generate_prompts_vqa(
    system_prompt: str,
    image_prompt: str,
    image_path: str,
    api_key: str,
    model: str,
    batch_size: int,
    max_tokens: int,
    temperature: float,
) -> list | str | None:
    """Generate prompts using OpenAI's chat completion API with an image."""
    client = OpenAI(api_key=api_key)

    # Read & (optionally) downscale image for token/cost; keep detail
    encoded_image = ""
    if image_path and os.path.exists(image_path):
        img = Image.open(image_path).convert("RGB")
        # Keep aspect ratio; max dimension ~1024 (256 was too destructive for fine cues)
        img.thumbnail((256, 256))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        encoded_image = base64.b64encode(buf.getvalue()).decode("utf-8")
    else:
        raise FileNotFoundError(f"Image not found: {image_path}")

    # User content = text + image part (not plain text base64)
    user_content = [
        {
            "type": "text",
            "text": (
                "Image attached below. Treat the image as the only authoritative evidence. "
                "Follow the system guidelines and output valid JSON only."
            ),
        },
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{encoded_image}"},
        },
    ]

    resp = client.chat.completions.create(
        model=model,  # e.g., "gpt-4o" or another vision-capable model
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        max_tokens=max_tokens,
        temperature=temperature,
        # n=batch_size  # if you actually want multiple generations
    )

    # Return one or many generations depending on n
    outputs = []
    for choice in resp.choices:
        msg = getattr(choice, "message", None)
        if msg and msg.content:
            outputs.append(msg.content.strip())
    return outputs if len(outputs) > 1 else outputs[0] if outputs else ""
