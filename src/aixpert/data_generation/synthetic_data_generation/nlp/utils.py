"""Utility functions for synthetic data generation in NLP tasks."""

import functools
import json
import os
from time import sleep
from typing import Callable, List, ParamSpec, TypeVar, cast

import openai


# Type variable for decorator
P = ParamSpec("P")
T = TypeVar("T", bound=openai.types.responses.response.Response)


# TODO(Ananya): Move to a dedicated decorators file.
def retry(num_retries: int) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Retry number of times if the response is invalid."""

    def decorator_retry(func: Callable[P, T]) -> Callable[P, T]:
        """Retry a function call if the response is invalid."""

        def is_valid(response: openai.types.responses.response.Response) -> bool:
            """Check if the response is valid."""
            return (
                not response.output_text.strip().startswith("I’m sorry,")
                or response.output_text.strip().startswith("I cannot")
                or response.output_text.strip().startswith("I am unable")
            )

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            """Run function num_retries times."""
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
    """Save results to a JSON file."""
    folder = os.path.dirname(filename)
    if not os.path.exists(folder):
        os.makedirs(folder)

    with open(filename, "w") as f:
        json.dump(results, f, indent=4)


def load_checkpoint(
    checkpoint_dir: str = "checkpoints",
    file_type: str = "checkpoints",
    domain: str = "hiring",
    risk: str = "bias_discrimination",
) -> List[dict]:
    """Load the latest checkpoint from the specified directory."""
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

    print(f"Loading scenes from checkpoint: {latest_checkpoint}")

    return scenes
