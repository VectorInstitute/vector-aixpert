"""Image Generation Flow File."""

import os

from crewai.flow.flow import Flow, listen, start
from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()


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
