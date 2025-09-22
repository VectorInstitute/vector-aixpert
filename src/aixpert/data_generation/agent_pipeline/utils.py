"""Utility File for agentic flow."""

import system_prompt


def var_to_dict_prompts() -> tuple[dict, dict]:
    """Create variable to dictionary for prompts."""
    prompt_dict = {}
    prompt_vqa_dict = {}
    for name, value in vars(system_prompt).items():
        if not name.startswith("__"):  # skip built-ins
            if "prompt_vqa" in name:
                prompt_dict[name] = value
            else:
                prompt_vqa_dict[name] = value
    return prompt_dict, prompt_vqa_dict
