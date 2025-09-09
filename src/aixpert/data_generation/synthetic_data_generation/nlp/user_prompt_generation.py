"""Generate user prompts based on templates and demographics."""

import argparse
import itertools
import json
import re
from typing import List

import yaml
from prompt_template import demographics, user_prompt_templates


def generate_prompts(domain: str, risk: str) -> List[str]:
    """Generate user prompts based on the specified domain and risk."""
    templates = user_prompt_templates[domain][risk]
    pattern = re.compile(
        r"{gender\d*}|{age\d*}|{race\d*}|{ses\d*}|{work_place\d*}|{disability\d*}"
    )

    # Format the prompts with the required variables
    formatted_prompts = []
    for _, template in enumerate(templates):
        occurrences = pattern.findall(template)
        if len(occurrences) == 0:
            formatted_prompts.append(template)
            continue

        demographic = demographics[re.sub("[{}0-9]", "", occurrences[0])]
        combos = itertools.permutations(demographic, len(set(occurrences)))
        for combo in combos:
            formatted_prompt = template
            for i in range(len(combo)):
                formatted_prompt = formatted_prompt.replace(occurrences[i], combo[i])
            formatted_prompts.append(formatted_prompt)

    return formatted_prompts


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--yaml", type=str, default="config.yaml")

    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    domain, risk = config["domain"], config["risk"]

    user_prompts = generate_prompts(domain, risk)

    # Save results to a file
    with open(config["user_prompts_file"], "w") as f:
        json.dump(user_prompts, f, indent=4)
