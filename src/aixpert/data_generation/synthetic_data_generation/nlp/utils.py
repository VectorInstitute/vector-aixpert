"""Miscellaneous utility functions for synthetic data generation in NLP tasks."""

import functools
import json
import os
import random
from time import sleep
from typing import Any, Callable, List, Optional, ParamSpec, Tuple, TypeVar, cast

import openai
import yaml


# Type variable for decorator
P = ParamSpec("P")
T = TypeVar("T", bound=openai.types.responses.response.Response)


def retry(num_retries: int) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Retry number of times if the response is invalid.

    :param num_retries: (int) Number of retries.
    :return: (Callable) Decorator function with params.
    """

    def decorator_retry(func: Callable[P, T]) -> Callable[P, T]:
        """Retry a function call if the response is invalid.

        :param func: (Callable) Function to be decorated.
        :return: (Callable) Decorated function.
        """

        def is_valid(response: openai.types.responses.response.Response) -> bool:
            """Check if the response is valid.

            :param response: (openai.types.responses.response.Response) Response object.
            :return: (bool) True if valid, False otherwise.
            """
            return (
                not response.output_text.strip().startswith("I’m sorry,")
                or response.output_text.strip().startswith("I cannot")
                or response.output_text.strip().startswith("I am unable")
            )

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            """Run function num_retries times.

            :param args: (P.args) Positional arguments.
            :param kwargs: (P.kwargs) Keyword arguments.
            :return: (T) Response object.
            """
            response = func(*args, **kwargs)
            if is_valid(response):
                return response
            for i in range(num_retries):
                print(f"Num retries left: {num_retries - i}")
                print(f"Retrying {i + 1}...")
                sleep(2)  # Optional: Add a delay before retrying
                response = func(*args, **kwargs)
                if is_valid(response):
                    print(
                        rf"Response after retry {i + 1}: \{response.output_text.strip()}"
                    )
                    break
            return response

        return cast(Callable[P, T], wrapper)

    return cast(Callable[[Callable[P, T]], Callable[P, T]], decorator_retry)


def save_results(results: List[dict], filename: str = "results/results.json") -> None:
    """Save results to a JSON file.

    :param results: (List[dict]) List of results to be saved.
    :param filename: (str) Filename to save the results.
    :return: None
    """
    folder = os.path.dirname(filename)
    if not os.path.exists(folder):
        os.makedirs(folder)

    with open(filename, "w") as f:
        json.dump(results, f, indent=4)


# TODO: Redo logic after adding shuffling in inference
def load_checkpoint(
    checkpoint_dir: str = "checkpoints",
    file_type: str = "checkpoints",
    domain: str = "hiring",
    risk: str = "bias_discrimination",
) -> List[dict]:
    """Load the latest checkpoint from the specified directory.

    :param checkpoint_dir: (str) Directory where checkpoints are stored.
    :param file_type: (str) Type of file to load.
    :param domain: (str) Domain of the data.
    :param risk: (str) Risk type of the data.
    :return: (List[dict]) List of dict loaded from the checkpoint.
    """
    if not os.path.exists(checkpoint_dir):
        return []

    checkpoints = [
        fname
        for fname in os.listdir(checkpoint_dir)
        if fname.startswith(f"{file_type}_{domain}_{risk}_")
    ]

    if not checkpoints:
        return []

    scenes = []
    latest_checkpoint = max(
        checkpoints, key=lambda x: int(x.split("_")[-1].split(".")[0])
    )

    with open(os.path.join(checkpoint_dir, latest_checkpoint), "r") as f:
        scenes = json.load(f)

    print(f"Loading from checkpoint: {latest_checkpoint}")

    return scenes


def load_yaml(yaml_path: str) -> dict:
    """Load a YAML file and return its content as a dict.

    :param yaml_path: (str) Path to the YAML file.
    :return: (dict) Content of the YAML file.
    """
    try:
        with open(yaml_path, "r") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"File not found error: {e}")
        return {}

    return config


###### STAGE UTILS ######
# TODO: Move to a separate file in agentic refactoring
def shuffle_options(mcq: dict[str, Any]) -> Tuple[List[str], dict[str, Any]]:
    """Shuffle the options of the MCQ and return a new dict with shuffled keys.

    :param mcq: (dict) MCQ with options to be shuffled.
    :return: (dict) MCQ with shuffled options.
    """

    def is_option(key: str) -> bool:
        """Check if a key is a single alphabetical character (A, B, C, D...)."""
        return len(key) == 1 and key.isalpha()

    mcq_keys = mcq.keys()
    options = sorted([k for k in mcq_keys if is_option(k)])

    shuffled_opts: list[str] = random.sample(options, len(options))
    shuffled_ans: dict[str, Any] = {
        options[i]: mcq[shuffled_opts[i]] for i in range(len(options))
    }

    return shuffled_opts, shuffled_ans


def postprocess(text: str) -> dict:
    """Postprocess the response text to convert it to JSON.

    :param text: (str) Response text.
    :return: (dict) JSON object.
    """
    try:
        output = json.loads(text, strict=False)
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")
        output = "JSON Error"

    return output


###### OPENAI UTILS ######
# TODO: Move to a separate file in agentic refactoring
def get_client(api_key: str) -> openai.OpenAI:
    """Initialize and return the OpenAI client.

    :param api_key: (str) OpenAI API key.
    :return: (openai.OpenAI) OpenAI client.
    """
    return openai.OpenAI(api_key=api_key)


def create_payload(system_prompt: Optional[str | None], prompt: str) -> List[dict]:
    """Create the payload for the OpenAI API call.

    :param system_prompt: (Optional[str | None]) System prompt for the API call.
    :param prompt: (str) User prompt for the API call.
    :return: (List[dict]) Payload for the API call.
    """
    return [
        {
            "role": "system",
            "content": (system_prompt if system_prompt else "You are an AI assistant."),
        },
        {"role": "user", "content": prompt},
    ]


@retry(num_retries=3)
def get_response(
    client: openai.OpenAI,
    input: List[dict],
    model: str,
    max_output_tokens: int,
    temperature: float,
    schema: Any = None,
) -> openai.types.responses.response.Response:
    """Get the response from the OpenAI API.

    :param client: (openai.OpenAI) OpenAI client.
    :param input: (List[dict]) Input payload for the API call.
    :param model: (str) Model to be used for the API call.
    :param max_output_tokens: (int) Maximum number of output tokens.
    :param temperature: (float) Temperature for the API call.
    :param schema: (Any) JSON schema for the response.
    :return: (openai.types.responses.response.Response) Response from the API call.
    """
    params = {
        "model": model,
        "input": input,
        "max_output_tokens": max_output_tokens,  # 800
        "temperature": temperature,  # 1.2
    }
    if schema:
        params.update(
            {
                "text": {
                    "format": {"name": "scene", "type": "json_schema", "schema": schema}
                }
            }
        )

    return client.responses.create(**params)
