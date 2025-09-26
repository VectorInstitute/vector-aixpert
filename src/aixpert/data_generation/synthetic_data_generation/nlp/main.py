"""
Main script to generate synthetic NLP data using OpenAI API.

Generates scenes and multiple-choice questions (MCQs)
based on specified domain and risk type.
"""

import argparse
import json
import pprint
import sys
import time
from collections import OrderedDict
from typing import Any, List, Optional

import openai
import yaml
from decouple import Config, RepositoryEnv
from openai import OpenAI
from prompt_gen_utils import (
    generate_prompts_healthcare,
    generate_prompts_hiring,
    generate_prompts_legal,
)
from prompts import mcq_user_prompts, system_prompts
from schema import (
    MCQ,
    HealthcareBias,
    LegalBias,
    RepGapMCQ,
    Scene,
    SecurityRiskMCQ,
    ToxicMCQ,
)
from utils import (
    load_checkpoint,
    retry,
    save_results,
)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="NLP Synthetic Data Generation")
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to the configuration YAML file",
    )
    parser.add_argument(
        "--stage",
        type=str,
        default="all",
        choices=["all", "user_prompt_gen", "only_mcq", "only_scenes"],
        help="Stage of the pipeline to run",
    )

    return parser.parse_args()


def create_payload(system_prompt: Optional[str | None], prompt: str) -> List[dict]:
    """Create the payload for the OpenAI API call."""
    return [
        {
            "role": "system",
            "content": (system_prompt if system_prompt else "You are an AI assistant."),
        },
        {"role": "user", "content": prompt},
    ]


def get_schema(domain: str, risk: str) -> Optional[dict]:
    """Get the JSON schema for the specified domain and risk."""
    if domain == "hiring" and risk == "bias_discrimination":
        return Scene.model_json_schema()
    if domain == "legal" and risk == "bias_discrimination":
        return LegalBias.model_json_schema()
    if domain == "healthcare" and risk == "bias_discrimination":
        return HealthcareBias.model_json_schema()
    return None


def get_mcq_schema(risk: str) -> Optional[dict]:
    """Get the JSON schema for the specified risk type."""
    if risk == "bias_discrimination":
        return MCQ.model_json_schema()
    if risk == "toxicity":
        return ToxicMCQ.model_json_schema()
    if risk == "representation_gaps":
        return RepGapMCQ.model_json_schema()
    if risk == "security_risks":
        return SecurityRiskMCQ.model_json_schema()

    return None


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
    start_idx = scenes[-1]["id"] if scenes else 0

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

        schema = get_schema(domain, risk)
        response = get_response(
            client, payload, model, max_output_tokens, temperature, schema
        )
        if schema:
            output = postprocess(response.output[0].content[0].text)
        else:
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
        if checkpoint and idx == len(user_prompts):
            save_results(
                scenes, f"{checkpoint_dir}/checkpoints_{domain}_{risk}_{idx}.json"
            )
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

    start_idx = mcqs[-1]["id"] if mcqs else 0
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
        if isinstance(output, dict):
            mcqs[-1].update(output)
        else:
            mcqs[-1].update({"text": output})

        print(f"Generated MCQ: {mcqs[-1]}")
        # Save final checkpoint if this is the last scene
        if checkpoint and i == len(scenes) - 1:
            save_results(mcqs, f"{checkpoint_dir}/mcqs_{domain}_{risk}_{i + 1}.json")

    return mcqs


def run_prompt_generation(domain: str, risk: str) -> List[str]:
    """Generate user prompts for a domain and risk type."""
    if domain == "hiring":
        user_prompts = generate_prompts_hiring(domain, risk)
    elif domain == "legal":
        user_prompts = generate_prompts_legal(domain, risk)
    elif domain == "healthcare":
        user_prompts = generate_prompts_healthcare(domain, risk)

    return user_prompts


def run_scene_generation(
    config: dict, model: str, api_key: str, domain: str, risk: str
) -> List[dict]:
    """Generate scenes for a domain and risk type."""
    client = OpenAI(api_key=api_key)
    print("OpenAI client initialized successfully.")

    model = config["model"]
    max_output_tokens = config["max_output_tokens"]
    temperature = config["temperature"]

    system_prompt = system_prompts[domain][risk]

    print(
        f"Model: {model}, Max Output Tokens: {max_output_tokens}, \
          Temperature: {temperature}"
    )

    with open(config["user_prompts_file"], "r") as f:
        user_prompts = json.load(f)

    return generate_text(
        client,
        user_prompts,
        system_prompt,
        model,
        max_output_tokens,
        temperature,
        checkpoint=False,
    )


def run_mcq_generation(
    config: dict, model: str, api_key: str, domain: str, risk: str
) -> List[dict]:
    """Generate MCQs for the given scenes for a domain and risk type."""
    client = OpenAI(api_key=api_key)
    print("OpenAI client initialized successfully.")

    model = config["model"]
    max_output_tokens = config["max_output_tokens"]
    temperature = config["temperature"]

    mcq_prompts = mcq_user_prompts[domain][risk]

    with open(config["scenes_file"], "r") as f:
        scenes = json.load(f)

    schema = get_mcq_schema(risk)
    return generate_mcq(
        client,
        mcq_prompts,
        scenes,
        model,
        max_output_tokens,
        temperature,
        schema,
        checkpoint=True,
    )


if __name__ == "__main__":
    args = parse_args()

    # Load config from YAML
    try:
        with open(args.config, "r") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"File not found error: {e}")
        sys.exit(1)

    # Load environment config
    env = Config(RepositoryEnv(config["repository"] + "/.env"))
    api_key = env("OPENAI_API_KEY", default=False)

    model = config["model"]
    domain, risk = config["domain"], config["risk"]

    if args.stage in ["all", "user_prompt_gen"]:
        print("STAGE 1: User Prompt Generation")
        print(f"Domain: {domain} Risk: {risk}")
        user_prompts = run_prompt_generation(domain, risk)
        save_results(user_prompts, f"{config['user_prompts_file']}")

    if args.stage in ["all", "only_scenes"]:
        print("STAGE 2: Scene Generation")
        print(f"Domain: {domain} Risk: {risk}")
        scenes = run_scene_generation(config, model, api_key, domain, risk)
        save_results(scenes, config["scenes_file"])

    # TODO (Ananya): Add logic for generating only MCQs with
    # and without generating scenes
    if args.stage in ["all", "only_mcq"]:
        print("STAGE 3: MCQ Generation")
        print(f"Domain: {domain} Risk: {risk}, Model: {model}")
        mcqs = run_mcq_generation(config, model, api_key, domain, risk)
        save_results(mcqs, config["mcq_file"])
