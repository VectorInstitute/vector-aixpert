"""Image Generation Flow File."""

import base64
import os
from contextlib import suppress
from pathlib import Path
from typing import Any

import requests
from crewai.flow.flow import Flow, listen, start
from dotenv import load_dotenv
from google import genai
from google.genai import types
from openai import OpenAI
from openai.types import ImagesResponse
from utils import load_config


load_dotenv()
config_path = Path(__file__).resolve().parents[2]


class OpenAIImageGenerationFlow(Flow):  # type: ignore
    """Generate Images using OpenAI."""

    description: str = "Generates images using Dalle model."
    model_name: str = "dall-e-3"
    number_of_images: int = 1
    quality: str = "standard"
    style: str = "vivid"
    img_size: str = "1024x1024"
    person_generation: str = "ALLOW_ALL"
    n: int = 1

    def __init__(self, prompt: str, file_name: str) -> None:
        """Initialize the class."""
        super().__init__()
        self.prompt = prompt
        self.file_name = file_name
        yaml_config = load_config(config_path, "config.yaml")
        self.model_name = yaml_config["dalle"].get("model", "dall-e-3")  # Model choice
        self.quality = yaml_config["dalle"].get(
            "quality", "standard"
        )  # Quality setting
        self.style = yaml_config["dalle"].get("style", "vivid")  # Style setting
        self.img_size = yaml_config["dalle"].get("img_size", "1024x1024")

    @start()  # type: ignore
    def generate_image(self) -> ImagesResponse:
        """Generate image using openai client."""
        client = OpenAI()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        print("Using OpenAI API Key from environment variable.")
        client.api_key = api_key
        return client.images.generate(
            model=self.model_name,
            prompt=self.prompt,
            style=self.style,  # Comment if using gpt-image-1
            size=self.img_size,
            n=1,
        )

    @listen(generate_image)  # type: ignore
    def save_image(self, response: ImagesResponse) -> str:
        """Save image in specified path."""
        image_data = response.data[0]
        try:
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
        except Exception as e:
            print(f"Error generating image: {e}")
            if response and hasattr(response, "data"):
                with suppress(Exception):
                    print(f"Full response:\n{response}")
            raise
        with open(self.file_name, "wb") as img_file:
            img_file.write(image_bytes)
        return "successful"


class GeminiImageGenerationFlow(Flow):  # type: ignore
    """Generates images using Gemini's model."""

    # model = "gpt-4o-mini"
    description: str = "Generates images using Gemini's model."
    model: str = "imagen-4.0-generate-001"
    number_of_images: int = 1
    sample_image_size: str = "1K"
    aspect_ratio: str = "1:1"
    person_generation: str = "ALLOW_ALL"
    n: int = 1

    def __init__(self, prompt: str, file_name: str) -> None:
        """Initialize the class."""
        super().__init__()
        self.prompt = prompt
        self.file_name = file_name
        yaml_config = load_config(config_path, "config.yaml")
        self.model = yaml_config["gemini"].get(
            "model", "imagen-4.0-generate-001"
        )  # Model choice
        self.number_of_images = yaml_config["gemini"].get(
            "numberOfImages", 1
        )  # Number of images to generate per prompt
        self.img_size = yaml_config["gemini"].get(
            "sampleImageSize", "1024x1024"
        )  # Image size
        self.aspect_ratio = yaml_config["gemini"].get(
            "aspectRatio", "1:1"
        )  # Aspect ratio
        self.person_generation = yaml_config["gemini"].get(
            "personGeneration", "ALLOW_ALL"
        )

    @start()  # type: ignore
    def generate_image(self) -> types.GenerateImagesResponse:
        """Generate Images based on the prompt."""
        client = genai.Client()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Missing required environment variables: GOOGLE_API_KEY")
        client.api_key = api_key
        print("Starting flow")
        # Each flow state automatically gets a unique ID
        print(f"Flow State ID: {self.state['id']}")
        print(self.prompt)
        return client.models.generate_images(
            model=self.model,
            prompt=self.prompt,
            config=types.GenerateImagesConfig(
                number_of_images=self.number_of_images,
                image_size=self.sample_image_size,  # "1K" or "2K"
                aspect_ratio=self.aspect_ratio,  # "1:1","3:4","4:3","9:16","16:9"
                # person_generation=person_generation,
                # # "ALLOW_ALL" | "ALLOW_ADULT" | "DONT_ALLOW"
                # safety_filter_level="BLOCK_ONLY_HIGH",
                # # optional; omit to use defaults
            ),
        )

    @listen(generate_image)  # type: ignore
    def save_image(self, response: types.GenerateImagesResponse) -> str:
        """Save Images in the specified path."""
        # output_filename = f"image_.png"
        with open(self.file_name, "wb") as img_file:
            img_file.write(response.generated_images[0].image.image_bytes)
        return "successful"


class ImageGenerationFlow(Flow):  # type: ignore
    """Factory flow for image generation."""

    def __init__(self, model_type: str, prompt: str, file_name: str) -> None:
        """Initialize the class."""
        super().__init__()
        self.specific_flow = self._instantiate_subflow(model_type, prompt, file_name)

    def _instantiate_subflow(self, model_type: str, *args: Any) -> Any:
        model_classes = {
            "gemini": GeminiImageGenerationFlow,
            "openai": OpenAIImageGenerationFlow,
        }

        if model_type not in model_classes:
            raise ValueError(f"Unsupported model type: {model_type}")

        return model_classes[model_type](*args)

    @start()  # type: ignore
    def generate_image(self) -> Any:
        """Generate Images based on the prompt."""
        return self.specific_flow.generate_image()

    @listen(generate_image)  # type: ignore
    def save_image(self, response: Any) -> str:
        """Save Images in the specified path."""
        self.specific_flow.save_image(response)
        return "successful"
