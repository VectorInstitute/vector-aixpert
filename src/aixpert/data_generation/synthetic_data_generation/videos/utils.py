"""Utility functions for video generation and prompt handling."""

# Standard libraries
import functools
import json
import os
import random
import time
from typing import Callable, Optional, ParamSpec, TypeVar, cast

import yaml
from google import genai
from google.genai import types


P = ParamSpec("P")
T = TypeVar("T")


def retry_operation(
    *,
    num_retries: int = 3,
    base_delay_seconds: float = 5.0,
    max_delay_seconds: float = 30.0,
    treat_falsey_as_failure: bool = True,
    on_retry: Optional[Callable[[int, Optional[BaseException]], None]] = None,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Retries a function on exception *or* falsey result (if enabled).

    Uses exponential backoff with jitter.

    Args:
        num_retries: Number of retry *attempts* after the initial try.
        base_delay_seconds: Base delay for first retry.
        max_delay_seconds: Max cap for the backoff delay.
        treat_falsey_as_failure: If True, retries when result evaluates to False.
        on_retry: Optional callback receiving (attempt_number, last_exception)
                  where attempt_number starts at 1 for the first retry.
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            last_exc: Optional[BaseException] = None

            for attempt in range(num_retries + 1):  # 0 = initial try
                try:
                    result = func(*args, **kwargs)
                    if not (treat_falsey_as_failure and not result):
                        return result  # success
                    # falsey result is treated as failure
                    last_exc = None
                except BaseException as e:
                    last_exc = e

                # decide whether to retry or raise
                if attempt == num_retries:
                    # exhausted
                    if last_exc:
                        raise last_exc
                    raise RuntimeError(
                        f"{func.__name__} returned no result after {num_retries + 1} attempts"
                    )

                # compute backoff with jitter
                delay = min(max_delay_seconds, base_delay_seconds * (2**attempt))
                delay = delay * (0.5 + random.random())  # jitter: 0.5x–1.5x
                if on_retry:
                    on_retry(attempt + 1, last_exc)
                elif last_exc:
                    print(
                        f"[retry {attempt + 1}/{num_retries}] {func.__name__} error: {last_exc}. Retrying in {delay:.1f}s…"
                    )
                else:
                    print(
                        f"[retry {attempt + 1}/{num_retries}] {func.__name__} returned no result. Retrying in {delay:.1f}s…"
                    )
                time.sleep(delay)

            # unreachable
            raise RuntimeError("Unexpected retry loop exit")

        return cast(Callable[P, T], wrapper)

    return decorator


def load_config(config_path: str) -> dict:
    """Load configuration from a YAML file."""
    try:
        with open(config_path, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Configuration file {config_path} not found.") from e
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML file {config_path}: {e}") from e


def load_prompt_path(prompt_yaml_path: str, domain: str, risk: str) -> str:
    """Load prompt path from a YAML file."""
    try:
        with open(prompt_yaml_path, "r") as file:
            prompts_dict = yaml.safe_load(file)
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Prompt YAML file {prompt_yaml_path} not found."
        ) from e
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML file {prompt_yaml_path}: {e}") from e

    try:
        return prompts_dict["prompts"][domain][risk]
    except KeyError as e:
        raise KeyError(
            f"Prompt for domain '{domain}' and risk '{risk}' not found in {prompt_yaml_path}"
        ) from e


def load_prompt(prompt_yaml: str, domain: str, risk: str) -> list:
    """Load prompts from a JSONL file based on domain and risk."""
    # Prompt_path is a jsonl file where each line is a JSON object
    # that has domain, risk, and video_prompt keys.
    matching_prompts = []
    prompts_path = load_prompt_path(prompt_yaml, domain, risk)

    try:
        with open(prompts_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    prompt = json.loads(line)
                    if prompt.get("domain") == domain and prompt.get("risk") == risk:
                        matching_prompts.append(prompt)
                except json.JSONDecodeError as e:
                    print(f"Skipping malformed JSON line: {e}")
    except FileNotFoundError:
        print(f"File not found: {prompts_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return matching_prompts


def build_checkpoint_path(domain: str, risk: str) -> str:
    """Build a checkpoint file path based on domain and risk."""
    os.makedirs("checkpoints", exist_ok=True)
    return os.path.join("checkpoints", f"checkpoint_{domain}_{risk}_videos.txt")


# Load checkpoint from a file
def load_checkpoint(checkpoint_file: str) -> tuple[int, list]:
    """Load the last processed index from a checkpoint file."""
    if not os.path.exists(checkpoint_file):
        # Create an empty checkpoint file
        with open(checkpoint_file, "w") as f:
            f.write(json.dumps({"last_processed_index": -1, "video_names": []}))
            print(f"Checkpoint file created: {checkpoint_file}")
            return -1, []

    # Load the last processed index and video names
    with open(checkpoint_file, "r") as f:
        checkpoint_data = json.load(f)
    last_processed_index = checkpoint_data.get("last_processed_index", -1)
    video_names = checkpoint_data.get("video_names", [])
    print(f"Resuming from index {last_processed_index + 1} with videos: {video_names}")
    return last_processed_index, video_names


# Save checkpoint to a file
def save_checkpoint(
    checkpoint_file: str, last_processed_index: int, video_names: list
) -> None:
    """
    Save the current processing index to a checkpoint file.

    This allows resuming from the last processed prompt in case of interruptions.
    """
    with open(checkpoint_file, "w") as f:
        checkpoint_data = {
            "last_processed_index": last_processed_index,
            "video_names": video_names,
        }
        f.write(json.dumps(checkpoint_data))
    print(
        f"Checkpoint saved at index {last_processed_index} with videos: {video_names}"
    )


@retry_operation(
    num_retries=3,
    base_delay_seconds=5,
    max_delay_seconds=20,
    treat_falsey_as_failure=True,
)
def save_video(
    client: genai.Client,
    video: types.GeneratedVideo,
    output_path: str,
    video_index: int,
) -> Optional[str]:
    """Download and save a generated video to the specified path."""
    try:
        # validate object presence
        video_obj = getattr(video, "video", None)
        video_uri = getattr(video_obj, "uri", None)
        if not video_obj or not video_uri:
            raise ValueError("GeneratedVideo.video or its uri is missing")

        print(f"Downloading video {video_index} from {video_uri}")
        client.files.download(file=video_obj)

        # Save the video
        video_obj.save(output_path)
        print(f"Video {video_index} saved as: {output_path}")

        # verify
        if not os.path.exists(output_path):
            raise IOError("File not found after save()")
        if os.path.getsize(output_path) == 0:
            raise IOError("Saved file is empty")

        return output_path  # indicate success

    except Exception as e:
        print(f"Error downloading or saving video {video_index}: {e}")
        return None  # indicate failure


def save_videos(
    client: genai.Client,
    videos: list[types.GeneratedVideo],
    folder_name: str,
    domain: str,
    risk: str,
    index: int,
    checkpoint_file: str,
) -> None:
    """Save multiple generated videos and update the checkpoint."""
    video_names: list[str] = []
    for n, video in enumerate(videos):
        # validate object presence
        video_uri = getattr(getattr(video, "video", None), "uri", None)
        if not video_uri:
            raise RuntimeError(
                f"Video {n} was not generated successfully (missing uri)."
            )

        video_name = f"{domain}_{risk}_video_{index + 1}_{n + 1}.mp4"
        output_path = os.path.join(folder_name, video_name)

        # save with retries (handle inside save_video)
        result_path = save_video(client, video, output_path, n + 1)
        if not result_path:
            raise Exception(f"Failed to save video {n + 1}. Checkpoint not updated.")

        video_names.append(video_name)

    # Update checkpoint only if all videos were saved successfully.
    save_checkpoint(checkpoint_file, index, video_names)


# Video Generation - Veo by Google
@retry_operation(
    num_retries=3,
    base_delay_seconds=15,
    max_delay_seconds=60,
    treat_falsey_as_failure=True,
)
def generate_video_veo(
    veo_params: dict,
    prompt: str,
    # number_of_videos: int, # TODO: Update this parameter multiple video generation
    duration_seconds: int = 8,
    negative_prompt: Optional[str] = None,
) -> Optional[tuple[genai.Client, list[types.GeneratedVideo]]]:
    """Generate a video using Gemini's video generation API."""
    client = genai.Client(api_key=veo_params["api_key"])

    operation = client.models.generate_videos(
        model=veo_params.get("model_name"),
        prompt=prompt,
        config=types.GenerateVideosConfig(
            aspect_ratio=veo_params.get("aspect_ratio"),
            # number_of_videos=params.get("number_of_videos"), # TODO: Not supported yet
            person_generation=veo_params.get("person_generation"),
            negative_prompt=negative_prompt,
            # duration_seconds=params.get("duration_seconds"), # TODO: Not supported yet
        ),
    )

    # Waiting for the video(s) to be generated
    while not operation.done:
        time.sleep(20)
        operation = client.operations.get(operation)
        print(operation)

    result = operation.result
    if not result:
        print("Error occurred while generating video.")
        return None

    generated_videos = result.generated_videos
    if not generated_videos:
        print("No videos were generated.")
        return None

    return client, generated_videos
