"""file for loading text based llms."""

from typing import Any

from llm_factory import load_llm


model_config = {
    "gemini": {"model": "GEMINI_MODEL", "api_key": "GOOGLE_API_KEY"},
    "grok": {"model": "GROK_MODEL", "api_key": "XAI_API_KEY"},
}


def load_text_llm(model_name: str) -> Any:
    """Load a text based llm."""
    return load_llm(
        model_config[model_name]["model"], model_config[model_name]["api_key"]
    )
