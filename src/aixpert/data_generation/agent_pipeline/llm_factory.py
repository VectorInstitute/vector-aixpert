"""Factory method for loading llm."""

import os

from crewai import LLM
from dotenv import load_dotenv


load_dotenv()


def load_llm(model_env_var: str, api_key_env_var: str) -> LLM:
    """
    Load an LLM instance from environment variables.

    Raise ValueError if required env vars are missing.
    """
    model = os.getenv(model_env_var)
    api_key = os.getenv(api_key_env_var)

    if not model or not api_key:
        raise ValueError(
            f"Missing required environment variables: "
            f"{' and '.join([v for v, val in [(model_env_var, model), (api_key_env_var, api_key)] if not val])}"
        )

    temperature = float(os.getenv("TEMPERATURE", "0.7"))  # config.yaml
    max_tokens = int(os.getenv("MAX_TOKENS", "8192"))  # config.yaml

    return LLM(
        model=model, temperature=temperature, max_tokens=max_tokens, api_key=api_key
    )
