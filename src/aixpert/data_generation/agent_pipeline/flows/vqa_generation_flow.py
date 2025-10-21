"""VQA Generation Flow File."""

import base64
import io
import json
import os
import re

from crewai.flow.flow import Flow, listen, start
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image


load_dotenv()


class GeminiVQAGenerationFlow(Flow):  # type: ignore
    """Generates VQA using Gemini's model."""

    # model = "gpt-4o-mini"
    description: str = "Generates images using Gemini's model."
    model: str = "gemini-2.5-pro"
    n: int = 1

    def __init__(self, prompt: str, file_name: str, parsed: dict) -> None:
        """Initialize the required variables."""
        super().__init__()
        self.prompt = prompt
        self.file_name = file_name
        self.parsed = parsed

    @start()  # type: ignore
    def generate_vqa(self) -> types.GenerateContentResponse:
        """Generate VQA based on the prompt and image."""
        client = genai.Client()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Missing required environment variables: GOOGLE_API_KEY")
        client.api_key = api_key
        print("Starting flow")
        # Each flow state automatically gets a unique ID
        print(f"Flow State ID: {self.state['id']}")
        print(self.prompt)
        encoded_image = ""
        if self.parsed["image_path"] and os.path.exists(self.parsed["image_path"]):
            img = Image.open(self.parsed["image_path"]).convert("RGB")
            img.thumbnail((256, 256))
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            encoded_image = base64.b64encode(buf.getvalue()).decode("utf-8")
        else:
            raise FileNotFoundError(f"Image not found: {self.parsed['image_path']}")
        return client.models.generate_content(
            model=self.model,
            contents=[
                types.Part.from_bytes(
                    data=encoded_image,
                    mime_type="image/png",
                ),
                "Image attached below. Treat the image as the only authoritative evidence. \
             Follow the system guidelines and output valid JSON only.",
            ],
            config=types.GenerateContentConfig(
                system_instruction=self.prompt,
                max_output_tokens=8192,
                temperature=0.7,
            ),
        )

    @listen(generate_vqa)  # type: ignore
    def save_vqa(self, response: types.GenerateContentResponse) -> str:
        """Save the generated VQA."""
        # output_filename = f"image_.png"
        print(response.text)
        content = (
            "\n".join(response.text)
            if isinstance(response.text, list)
            else response.text
        )
        metadata = re.findall(r"```json(.*)```", content, re.DOTALL)
        assert len(metadata) == 1, "there should be only one metadata generated"
        try:
            metadata = json.loads(metadata[0])
        except json.JSONDecodeError as e:
            print(f"Skipping invalid JSON: {e}")
            return "skipping"
        self.parsed["vqa"] = metadata
        with open(self.file_name, "a", encoding="utf-8") as f:
            json_line = json.dumps(self.parsed, ensure_ascii=False)
            f.write(json_line + "\n")
        # with open(self.file_name, "wb") as img_file:
        #       img_file.write(response.generated_images[0].image.image_bytes)
        return "successful"


# flow = GeminiImageGenerationFlow("./","test.png")
# flow.plot()
# result = flow.kickoff()

# rint(f"Generated fun fact: {result}")
