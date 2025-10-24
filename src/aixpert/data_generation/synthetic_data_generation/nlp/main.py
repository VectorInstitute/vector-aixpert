"""
Main script to generate synthetic NLP data using OpenAI API.

Generates scenes, multiple-choice questions (MCQs) and answers
based on specified domain and risk type.
"""

import argparse
import json
import random
import sys
import time
from collections import OrderedDict
from typing import Any, List

import openai
from decouple import Config, RepositoryEnv
from prompt_gen_utils import run_prompt_generation
from prompts import (
    get_answer_prompt,
    get_mcq_user_prompt,
    get_risk_mcq,
    get_system_prompt,
)
from schema import (
    get_answer_schema,
    get_mcq_schema,
    get_scene_schema,
)
from utils import (
    create_payload,
    get_client,
    get_response,
    load_checkpoint,
    load_yaml,
    postprocess,
    save_results,
    shuffle_options,
)


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    :return (argparse.Namespace): Parsed arguments.
    """
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
        choices=["all", "user_prompt_gen", "only_mcqs", "only_scenes", "only_answers"],
        help="Stage of the pipeline to run",
    )

    return parser.parse_args()


def generate_scenes(
    client: openai.OpenAI,
    user_prompts: list,
    system_prompt: str,
    model: str,
    max_output_tokens: int,
    temperature: float,
    schema: Any = None,
    checkpoint: bool = False,
    checkpoint_dir: str = "checkpoints",
) -> List[dict]:
    """Generate scenes using user and system prompts via API calls.

    :param client: (openai.OpenAI) OpenAI client instance.
    :param user_prompts: (list) List of user prompts for scene generation.
    :param system_prompt: (str) Domain and risk specific system prompt.
    :param model: (str) OpenAI model name.
    :param max_output_tokens: (int) Maximum output tokens.
    :param temperature: (float) Token generation temperature.
    :param schema: (Any) Pydantic JSON schema for response validation.
    :param checkpoint: (bool) Flag to use checkpoints.
    :param checkpoint_dir: (str) Directory path to save checkpoints.
    :return: (List[dict]) Generated scenes.
    """
    print(f"Generating scenes with model: {model}")

    scenes = (
        load_checkpoint(checkpoint_dir=checkpoint_dir, domain=domain, risk=risk)
        if checkpoint
        else []
    )
    start_idx = scenes[-1]["id"] if scenes else 0

    print(f"Starting from scene ID: {start_idx}")
    print(f"Total user prompts: {len(user_prompts)}")

    for idx, user_prompt in enumerate(user_prompts[start_idx:], start=start_idx + 1):
        time.sleep(0.5)  # To avoid rate limiting
        if checkpoint and idx % 10 == 0:
            save_results(
                scenes, f"{checkpoint_dir}/checkpoints_{domain}_{risk}_{idx}.json"
            )

        print(f"Generating scene {idx} using prompt: {user_prompt}..")
        payload = create_payload(system_prompt, user_prompt)
        response = get_response(
            client, payload, model, max_output_tokens, temperature, schema
        )

        # postprocess the response
        if schema:
            output = postprocess(response.output[0].content[0].text)
        else:
            output = response.output_text.strip()

        print(f"\nGenerated response: {output}")
        scenes.append(
            OrderedDict(
                {
                    "id": idx,
                    "prompt": user_prompt,
                }
            )
        )

        # Update the scene with output
        if isinstance(output, dict):
            scenes[-1].update(output)
        else:
            scenes[-1].update({"text": output})

        if checkpoint and idx == len(user_prompts):
            save_results(
                scenes, f"{checkpoint_dir}/checkpoints_{domain}_{risk}_{idx}.json"
            )
    return scenes


def generate_mcq(
    client: openai.OpenAI,
    mcq_prompts: str,
    scenes: List[dict],
    model: str,
    max_output_tokens: int,
    temperature: float,
    schema: Any = None,
    checkpoint: bool = False,
    checkpoint_dir: str = "checkpoints",
) -> List[dict]:
    """Generate MCQs for the given scenes via API calls.

    :param client: (openai.OpenAI) OpenAI client instance.
    :param mcq_prompts: (list) List of mcq prompts for scene generation.
    :param scenes: (dict) List of scenes for which MCQs are generated.
    :param model: (str) OpenAI model name.
    :param max_output_tokens: (int) Maximum output tokens.
    :param temperature: (float) Token generation temperature.
    :param schema: (Any) Pydantic JSON schema for response validation.
    :param checkpoint: (bool) Flag to use checkpoints.
    :param checkpoint_dir: (str) Directory path to save checkpoints.
    :return: (List[dict]) MCQs.
    """
    print(f"Generating MCQs with model: {model}")

    mcqs = (
        load_checkpoint(
            checkpoint_dir=checkpoint_dir, file_type="mcqs", domain=domain, risk=risk
        )
        if checkpoint
        else []
    )
    start_idx = mcqs[-1]["id"] if mcqs else 0

    print(f"Starting from scene ID: {start_idx}")
    print(f"Total mcq prompts: {len(mcqs)}")

    for i in range(start_idx, len(scenes)):
        print(f"Generating MCQs for scene {i}..")
        time.sleep(0.5)  # To avoid rate limiting
        if checkpoint and i % 10 == 0:
            save_results(mcqs, f"{checkpoint_dir}/mcqs_{domain}_{risk}_{i}.json")

        # Get response from API call
        payload = create_payload(None, mcq_prompts.format(scenario=scenes[i]["text"]))
        response = get_response(
            client, payload, model, max_output_tokens, temperature, schema=schema
        )

        # Postprocess the response
        output = postprocess(response.output[0].content[0].text)
        print(f"Output: {output}")

        # Append to mcqs
        mcqs.append(scenes[i])
        if isinstance(output, dict):
            mcqs[-1].update(output)
        else:
            mcqs[-1].update({"text": output})

        # Save final checkpoint if this is the last scene
        if checkpoint and i == len(scenes) - 1:
            save_results(mcqs, f"{checkpoint_dir}/mcqs_{domain}_{risk}_{i + 1}.json")
    return mcqs


def generate_answer(
    client: openai.OpenAI,
    answer_gen_prompt: str,
    mcqs: dict,
    model: str,
    max_output_tokens: int,
    temperature: float,
    schema: Any = None,
    checkpoint: bool = False,
    checkpoint_dir: str = "checkpoints",
) -> List[dict]:
    """Generate answers for the given MCQs via API calls.

    :param client: (openai.OpenAI) OpenAI client instance.
    :param answer_gen_prompt: (list) List of prompts for answer generation.
    :param mcqs: (str) List of MCQs for which answers are generated.
    :param model: (str) OpenAI model name.
    :param max_output_tokens: (int) Maximum output tokens.
    :param temperature: (float) Token generation temperature.
    :param schema: (Any) Pydantic JSON schema for response validation.
    :param checkpoint: (bool) Flag to use checkpoints.
    :param checkpoint_dir: (str) Directory path to save checkpoints.
    :return: (List[dict]) Generated answers.
    """
    print(f"Generating answers with model: {model}")

    answers = (
        load_checkpoint(
            checkpoint_dir=checkpoint_dir, file_type="answers", domain=domain, risk=risk
        )
        if checkpoint
        else []
    )

    processed_ids = {a["id"] for a in answers}
    print(f"Total answers already generated: {len(processed_ids)}")

    # Shuffle the MCQs to avoid positional bias
    for i in random.sample(range(len(mcqs)), len(mcqs)):
        if i in processed_ids:
            continue

        print(f"Generating answers for scene {i}..")
        time.sleep(0.5)  # To avoid rate limiting
        if checkpoint and len(processed_ids) % 10 == 0:
            save_results(
                answers,
                f"{checkpoint_dir}/answers_{domain}_{risk}_{len(processed_ids)}.json",
            )

        # Shuffle options to avoid positional bias
        shuffled_opts, shuffled_ans = shuffle_options(mcqs[i])

        # Get response from API call
        payload = create_payload(
            None,
            answer_gen_prompt.format(
                scenario=mcqs[i]["text"], mcq=mcqs[i]["MCQ"], options=str(shuffled_ans)
            ),
        )
        response = get_response(
            client, payload, model, max_output_tokens, temperature, schema=schema
        )

        # Postprocess the response
        output = postprocess(response.output[0].content[0].text)
        print(f"Output: {output}")

        # Append to answers
        answers.append(mcqs[i])

        if isinstance(output, dict):
            # Map back to original option
            org_index = list(shuffled_ans.keys()).index(output["answer"])
            output["answer"] = shuffled_opts[org_index]
            answers[-1].update(output)
        else:
            answers[-1].update({"text": output})

        print(f"Generated Answer: {answers[-1]}")

        # Add to processed ids
        processed_ids.add(i)

        # Save final checkpoint if this is the last scene
        if checkpoint and len(processed_ids) == len(mcqs) - 1:
            save_results(
                answers,
                f"{checkpoint_dir}/answers_{domain}_{risk}_{len(processed_ids)}.json",
            )

    return answers


def run_scene_generation(
    config: dict, api_key: str, domain: str, risk: str
) -> List[dict]:
    """Call scene generation for a domain and risk type.

    :param config: (dict) Configuration dictionary from CLI args.
    :param api_key: (str) OpenAI API key.
    :param domain: (str) Domain name.
    :param risk: (str) Risk type.
    :return: (List[dict]) Generated scenes.
    """
    client = get_client(api_key)
    print("OpenAI client initialized successfully.")

    system_prompt = get_system_prompt(domain, risk)
    schema = get_scene_schema(domain)

    with open(config["user_prompts_file"], "r") as f:
        user_prompts = json.load(f)

    return generate_scenes(
        client,
        user_prompts,
        system_prompt,
        config["model"],
        config["max_output_tokens"],
        config["temperature"],
        schema,
        checkpoint=False,
    )


def run_mcq_generation(
    config: dict, api_key: str, domain: str, risk: str
) -> List[dict]:
    """Call MCQ generation for a domain and risk type.

    :param config: (dict) Configuration dictionary from CLI args.
    :param api_key: (str) OpenAI API key.
    :param domain: (str) Domain name.
    :param risk: (str) Risk type.
    :return: (List[dict]) Generated MCQs.
    """
    client = get_client(api_key)
    print("OpenAI client initialized successfully.")

    with open(config["scenes_file"], "r") as f:
        scenes = json.load(f)

    # If risk is toxicity or representation gaps, use fixed MCQ template
    if risk in ["toxicity", "representation_gaps", "security_risks"]:
        mcqs = []
        for scene in scenes:
            mcqs.append(scene)
            mcqs[-1].update(get_risk_mcq(risk))
        return mcqs

    mcq_prompts = get_mcq_user_prompt(domain, risk)
    schema = get_mcq_schema(risk)

    return generate_mcq(
        client,
        mcq_prompts,
        scenes,
        config["model"],
        config["max_output_tokens"],
        config["temperature"],
        schema,
        checkpoint=False,
    )


def run_answer_generation(
    config: dict, api_key: str, domain: str, risk: str
) -> List[dict]:
    """Call answer generation for the given MCQs.

    :param config: (dict) Configuration dictionary from CLI args.
    :param api_key: (str) OpenAI API key.
    :param domain: (str) Domain name.
    :param risk: (str) Risk type.
    :return: (List[dict]) Generated answers.
    """
    client = get_client(api_key)
    print("OpenAI client initialized successfully.")

    answer_gen_prompt = get_answer_prompt(domain, risk)

    print(f"Loading MCQs from {config['mcq_data_file']}")
    with open(config["mcq_data_file"], "r") as f:
        mcqs = json.load(f)

    schema = get_answer_schema(risk)
    return generate_answer(
        client,
        answer_gen_prompt,
        mcqs,
        config["model"],
        config["max_output_tokens"],
        config["temperature"],
        schema,
        checkpoint=False,
    )


if __name__ == "__main__":
    """Main function to run the NLP data generation pipeline."""

    # Parse CLI arguments
    args = parse_args()

    # Load config from YAML
    config = load_yaml(args.config)
    if not config:
        sys.exit("Failed to load configuration. Exiting.")

    # Load security config
    env = Config(RepositoryEnv(config["repository"] + "/.env"))
    api_key = env("OPENAI_API_KEY", default=False)

    domain, risk = config["domain"], config["risk"]
    print(f"Domain: {domain} Risk: {risk}, Model: {config['model']}")

    # Stages of NLP data generation
    if args.stage in ["all", "user_prompt_gen"]:
        print("STAGE 1: User Prompt Generation")
        user_prompts = run_prompt_generation(domain, risk)
        save_results(user_prompts, f"{config['user_prompts_file']}")

    if args.stage in ["all", "only_scenes"]:
        print("STAGE 2: Scene Generation")
        scenes = run_scene_generation(config, api_key, domain, risk)
        save_results(scenes, config["scenes_file"])

    if args.stage in ["all", "only_mcqs"]:
        print("STAGE 3: MCQ Generation")
        mcqs = run_mcq_generation(config, api_key, domain, risk)
        save_results(mcqs, config["mcq_data_file"])

    if args.stage in ["all", "only_answers"]:
        print("STAGE 4: Answer Generation")
        answers = run_answer_generation(config, api_key, domain, risk)
        answers = sorted(answers, key=lambda x: x["id"])
        save_results(answers, config["answers_file"])
