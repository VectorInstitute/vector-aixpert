"""VQA Generation Flow File."""

import base64
import io
import json
import os
import re
from pathlib import Path
from typing import Any

from crewai.flow.flow import Flow, listen, start
from dotenv import load_dotenv
from google import genai
from google.genai import types
from openai import OpenAI
from openai.types.chat import ChatCompletion
from PIL import Image
from utils import load_config


load_dotenv()
config_path = Path(__file__).resolve().parents[2]


class OpenAIVQAGenerationFlow(Flow):  # type: ignore
    """Generates VQA using OpenAI's model."""

    description: str = "Generates images using Gemini's model."
    model: str = "gpt-4o"
    max_tokens: int = 2048
    temperature: float = 0.7

    n: int = 1

    def __init__(self, prompt: str, file_name: str, parsed: dict) -> None:
        """Initialize the class."""
        super().__init__()
        yaml_config = load_config(config_path, "config.yaml")
        self.model = yaml_config["gpt"].get("model", self.model)  # Model choice
        self.max_tokens = yaml_config["gpt"].get(
            "max_tokens", 2048
        )  # Max tokens for response
        self.temperature = yaml_config["gpt"].get("temperature", 0.7)
        self.prompt = prompt
        self.file_name = file_name
        self.parsed = parsed

    @start()  # type: ignore
    def generate_vqa(self) -> ChatCompletion:
        """Generate VQA based on the prompt and image."""
        # client = genai.Client()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Missing required environment variables: OPENAI_API_KEY")
        # client.api_key = api_key
        client = OpenAI(api_key=api_key)
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

        return client.chat.completions.create(
            model=self.model,  # e.g., "gpt-4o" or another vision-capable model
            messages=[
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": user_content},
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            # n=batch_size  # if you actually want multiple generations
        )

    @listen(generate_vqa)  # type: ignore
    def save_vqa(self, response: ChatCompletion) -> str:
        """Save the generated VQA."""
        # output_filename = f"image_.png"
        print(response)
        for choice in response.choices:
            msg = getattr(choice, "message", None)
            if msg and msg.content:
                output = msg.content.strip()
        content = "\n".join(output) if isinstance(output, list) else output
        vqa_content = re.findall(r"```json(.*)```", content, re.DOTALL)
        if len(vqa_content) != 1:
            vqa_content = [content]
        assert len(vqa_content) == 1, "there should be only one metadata generated"
        # metadata = re.findall(r"```json(.*)```", content, re.DOTALL)
        # assert len(metadata) == 1, "there should be only one metadata generated"
        try:
            vqa = json.loads(vqa_content[0])
        except json.JSONDecodeError as e:
            print(f"Skipping invalid JSON: {e}")
            return "skipping"
        self.parsed["vqa"] = vqa
        with open(self.file_name, "a", encoding="utf-8") as f:
            json_line = json.dumps(self.parsed, ensure_ascii=False)
            f.write(json_line + "\n")
        # with open(self.file_name, "wb") as img_file:
        #       img_file.write(response.generated_images[0].image.image_bytes)
        return "successful"


class GeminiVQAGenerationFlow(Flow):  # type: ignore
    """Generates VQA using Gemini's model."""

    # model = "gpt-4o-mini"
    description: str = "Generates images using Gemini's model."
    model: str = "gemini-2.5-pro"
    n: int = 1

    def __init__(self, prompt: str, file_name: str, parsed: dict) -> None:
        """Initialize the required variables."""
        super().__init__()
        yaml_config = load_config(config_path, "config.yaml")
        self.model = yaml_config["gemini_text"].get("model", self.model)  # Model choice
        if "/" in self.model:
            self.model = self.model.split("/")[1]
        # print(self.model)
        self.max_tokens = yaml_config["gemini_text"].get(
            "max_tokens", 2048
        )  # Max tokens for response
        self.temperature = yaml_config["gemini_text"].get("temperature", 0.7)
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


class VQAGenerationFlow(Flow):  # type: ignore
    """Factory Flow for the VQA Generation."""

    def __init__(
        self, model_type: str, prompt: str, file_name: str, parsed: dict
    ) -> None:
        """Initialize the class."""
        super().__init__()
        self.specific_flow = self._instantiate_subflow(
            model_type, prompt, file_name, parsed
        )

    def _instantiate_subflow(self, model_type: str, *args: Any) -> Any:
        model_classes = {
            "gemini": GeminiVQAGenerationFlow,
            "openai": OpenAIVQAGenerationFlow,
        }

        if model_type not in model_classes:
            raise ValueError(f"Unsupported model type: {model_type}")

        return model_classes[model_type](*args)

    @start()  # type: ignore
    def generate_vqa(self) -> Any:
        """Generate Images based on the prompt."""
        return self.specific_flow.generate_vqa()

    @listen(generate_vqa)  # type: ignore
    def save_vqa(self, response: Any) -> str:
        """Save Images in the specified path."""
        self.specific_flow.save_vqa(response)
        return "successful"


# flow = GeminiImageGenerationFlow("./","test.png")
# flow.plot()
# result = flow.kickoff()

# rint(f"Generated fun fact: {result}")
