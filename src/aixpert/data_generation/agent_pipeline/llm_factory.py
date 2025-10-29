"""Factory method for loading llm."""

import os
from pathlib import Path

from crewai import LLM
from dotenv import load_dotenv
from utils import load_config


load_dotenv()
config_path = Path(__file__).resolve().parents[1]


def load_llm(model_env_var: str, api_key_env_var: str, config_key_var: str) -> LLM:
    """
    Load an LLM instance from environment variables.

    Raise ValueError if required env vars are missing.
    """
    api_key = os.getenv(api_key_env_var)
    config_key = config_key_var
    if not api_key:
        raise ValueError(f"Missing required environment variables: {api_key_env_var}")
    yaml_config = load_config(config_path, "config.yaml")

    model = yaml_config[config_key].get("model")
    max_tokens = yaml_config[config_key].get(
        "max_tokens", 2048
    )  # Max tokens for response
    temperature = yaml_config[config_key].get("temperature", 0.7)
    return LLM(
        model=model, temperature=temperature, max_tokens=max_tokens, api_key=api_key
    )
