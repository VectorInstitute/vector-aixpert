"""Utility File for agentic flow."""

import json
import os

import system_prompt


def var_to_dict_prompts() -> tuple[dict, dict, dict]:
    """Create variable to dictionary for prompts."""
    prompt_dict = {}
    prompt_vqa_dict = {}
    prompt_metadata_dict = {}
    for name, value in vars(system_prompt).items():
        if not name.startswith("__"):  # skip built-ins
            if "metadata" in name:
                prompt_metadata_dict[name] = value
            elif "vqa" in name:
                prompt_vqa_dict[name] = value
            else:
                prompt_dict[name] = value
    return prompt_dict, prompt_vqa_dict, prompt_metadata_dict


def read_directory(path: str) -> list:
    """Return list of files from a path."""
    try:
        # List all entries in the directory
        entries = os.listdir(path)
        # print(f"Contents of '{path}':")
        file_names = []
        for entry in entries:
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                print(f"[DIR]  {entry}")
            else:
                file_names.append(full_path)
    except FileNotFoundError:
        print(f"Error: The directory '{path}' does not exist.")
    except PermissionError:
        print(f"Error: Permission denied to access '{path}'.")
    return file_names


def load_prompt(prompt_path: str) -> list:
    """Load prompts from a JSONL file based on domain and risk."""
    # Prompt_path is a jsonl file where each line is a JSON object
    # that has domain, risk, and image_prompt keys.
    matching_prompts = []

    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    prompt = json.loads(line)
                    # if prompt.get("domain") == domain and prompt.get("risk") == risk:
                    matching_prompts.append(prompt)
                except json.JSONDecodeError as e:
                    print(f"Skipping malformed JSON line: {e}")
    except FileNotFoundError:
        print(f"File not found: {prompt_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return matching_prompts[0] if len(matching_prompts) == 1 else matching_prompts
