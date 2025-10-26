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
    model = os.getenv(model_env_var)
    api_key = os.getenv(api_key_env_var)
    config_key = config_key_var
    if not model or not api_key:
        raise ValueError(
            f"Missing required environment variables: "
            f"{' and '.join([v for v, val in [(model_env_var, model), (api_key_env_var, api_key)] if not val])}"
        )
    yaml_config = load_config(config_path, "config.yaml")

    model = yaml_config[config_key].get("model", model)  # Model choice
    max_tokens = yaml_config[config_key].get(
        "max_tokens", 2048
    )  # Max tokens for response
    temperature = yaml_config[config_key].get("temperature", 0.7)
    return LLM(
        model=model, temperature=temperature, max_tokens=max_tokens, api_key=api_key
    )
