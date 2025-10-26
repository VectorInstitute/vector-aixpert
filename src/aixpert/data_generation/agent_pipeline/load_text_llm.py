"""file for loading text based llms."""

from typing import Any

from llm_factory import load_llm


model_config = {
    "openai": {
        "model": "OPENAI_MODEL",
        "api_key": "OPENAI_API_KEY",
        "config_key": "gpt",
    },
    "gemini": {
        "model": "GEMINI_MODEL",
        "api_key": "GOOGLE_API_KEY",
        "config_key": "gemini_text",
    },
    "grok": {"model": "GROK_MODEL", "api_key": "XAI_API_KEY", "config_key": "grok"},
}


def load_text_llm(model_name: str) -> Any:
    """Load a text based llm."""
    return load_llm(
        model_config[model_name]["model"],
        model_config[model_name]["api_key"],
        model_config[model_name]["config_key"],
    )
