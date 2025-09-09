"""
Main script to generate synthetic NLP data using OpenAI API.

Generates scenes and multiple-choice questions (MCQs)
based on specified domain and risk type.
"""

import argparse
import json
import pprint
import time
from collections import OrderedDict
from typing import Any, List, Optional

import openai
import yaml
from decouple import Config, RepositoryEnv
from openai import OpenAI
from prompts import mcq_user_prompts, system_prompts
from schema import MCQ, RepGapMCQ, Scene, ToxicMCQ
from utils import load_checkpoint, retry, save_results


def create_payload(system_prompt: Optional[str | None], prompt: str) -> List[dict]:
    """Create the payload for the OpenAI API call."""
    return [
        {
            "role": "system",
            "content": (system_prompt if system_prompt else "You are an AI assistant."),
        },
        {"role": "user", "content": prompt},
    ]


@retry(num_retries=3)  # type: ignore[misc]
def get_response(
    client: OpenAI,
    input: List[dict],
    model: str,
    max_output_tokens: int,
    temperature: float,
    schema: Any = None,
) -> openai.types.responses.response.Response:
    """Get the response from the OpenAI API."""
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


def postprocess(text: str) -> dict:
    """Postprocess the response text to convert it to JSON."""
    try:
        output = json.loads(text, strict=False)
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")
        output = "JSON Error"

    return output


def generate_text(
    client: OpenAI,
    user_prompts: list,
    system_prompt: str,
    model: str,
    max_output_tokens: int,
    temperature: float,
    checkpoint: bool = False,
    checkpoint_dir: str = "checkpoints",
) -> List[dict]:
    """Generate scenes for a domain and risk type with user prompts."""
    print(f"Generating text for domain: {domain}, risk: {risk}")

    scenes = (
        load_checkpoint(checkpoint_dir=checkpoint_dir, domain=domain, risk=risk)
        if checkpoint
        else []
    )
    start_idx = scenes[-1]["id"] - 1 if scenes else 0

    print(f"Starting from scene ID: {start_idx}")
    print(f"Total user prompts: {len(user_prompts)}")
    # TODO(Ananya): Add logic to handle API call + output format
    # based on domain and risk.
    for idx, user_prompt in enumerate(user_prompts[start_idx:], start=start_idx + 1):
        time.sleep(0.5)  # To avoid rate limiting
        print(f"Processing scene ID: {idx}, Prompt: {user_prompt}\n")
        if checkpoint and idx % 10 == 0:
            save_results(
                scenes, f"{checkpoint_dir}/checkpoints_{domain}_{risk}_{idx}.json"
            )

        print(f"Generating scene for prompt: {user_prompt}")
        print(f"Scene ID: {idx}, Prompt: {user_prompt}")
        payload = create_payload(system_prompt, user_prompt)

        if risk == "bias_discrimination":
            response = get_response(
                client,
                payload,
                model,
                max_output_tokens,
                temperature,
                Scene.model_json_schema(),
            )
            output = postprocess(response.output[0].content[0].text)
        else:
            response = get_response(
                client, payload, model, max_output_tokens, temperature
            )
            output = response.output_text.strip()

        print(f"Generated scene: {output}")
        scenes.append(
            OrderedDict(
                {
                    "id": idx,
                    "prompt": user_prompt,
                }
            )
        )
        if isinstance(output, dict):
            scenes[-1].update(output)
        else:
            scenes[-1].update({"text": output})

        pprint.pprint(scenes[-1])

    return scenes


def generate_mcq(
    client: OpenAI,
    mcq_prompts: str,
    scenes: dict,
    model: str,
    max_output_tokens: int,
    temperature: float,
    schema: Any = None,
    checkpoint: bool = False,
    checkpoint_dir: str = "checkpoints",
) -> List[dict]:
    """Generate MCQs for the given scenes for a domain and risk type."""
    mcqs = []
    if checkpoint:
        mcqs = load_checkpoint(
            checkpoint_dir=checkpoint_dir, file_type="mcqs", domain=domain, risk=risk
        )

    start_idx = mcqs[-1]["id"] - 1 if mcqs else 0
    for i in range(start_idx, len(scenes)):
        print(f"Sample {i + 1}:")
        print(f"Scenario: {scenes[i]['text']}")
        time.sleep(0.5)  # To avoid rate limiting

        if checkpoint and i % 10 == 0:
            save_results(mcqs, f"{checkpoint_dir}/mcqs_{domain}_{risk}_{i}.json")
        payload = create_payload(None, mcq_prompts.format(scenario=scenes[i]["text"]))
        response = get_response(
            client, payload, model, max_output_tokens, temperature, schema=schema
        )
        output = postprocess(response.output[0].content[0].text)

        print(f"Output: {output}")

        mcqs.append(scenes[i])
        mcqs[-1].update(output)
        print(f"Generated MCQ: {mcqs[-1]}")

    return mcqs


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--yaml", type=str, default="config.yaml")

    # Load config from YAML
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    # Load environment config
    env = Config(RepositoryEnv(config["repository"] + "/.env"))
    api_key = env("OPENAI_API_KEY", default=False)

    model = config["model"]
    max_output_tokens = config["max_output_tokens"]
    temperature = config["temperature"]
    domain, risk = config["domain"], config["risk"]

    print(
        f"Model: {model}, Max Output Tokens: {max_output_tokens}, \
          Temperature: {temperature}"
    )
    print("Step 1: Generating text with OpenAI client...")

    with open(config["user_prompts_file"], "r") as f:
        user_prompts = json.load(f)

    system_prompt = system_prompts[domain][risk]
    print("Loaded User prompts and System prompts.")

    client = OpenAI(api_key=api_key)
    print("OpenAI client initialized successfully.")

    scenes = generate_text(
        client,
        user_prompts,
        system_prompt,
        model,
        max_output_tokens,
        temperature,
        checkpoint=True,
    )

    save_results(scenes, f"results/scenes_{domain}_{risk}.json")

    # TODO (Ananya): Add logic for generating only MCQs with
    # and without generating scenes
    print("Step 2: Generating MCQs based on the generated scenes...")
    mcq_prompts = mcq_user_prompts[domain][risk]

    with open(f"results/scenes_{domain}_{risk}.json", "r") as f:
        scenes = json.load(f)
    if risk == "bias_discrimination":
        schema = MCQ.model_json_schema()
    elif risk == "toxicity":
        schema = ToxicMCQ.model_json_schema()
    else:
        schema = RepGapMCQ.model_json_schema()
    mcqs = generate_mcq(
        client,
        mcq_prompts,
        scenes,
        model,
        max_output_tokens,
        temperature,
        schema,
        checkpoint=True,
    )

    save_results(mcqs, f"results/mcqs_{domain}_{risk}.json")
