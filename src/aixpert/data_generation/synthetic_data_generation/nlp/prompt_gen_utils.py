"""Generate user prompts based on templates and demographics."""

import itertools
import re
from itertools import permutations, product
from typing import Any, List, Optional

from prompt_template import demographics, healthcare, legal, user_prompt_templates


# TODO(Ananya): Combine into single function with domain as argument (IF POSSIBLE)
def generate_prompts_hiring(domain: str, risk: str) -> List[str]:
    """Generate user prompts for hiring domain."""
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


def generate_prompts_legal(domain: str, risk: str) -> List[str]:
    """Generate user prompts for legal domain."""
    templates = user_prompt_templates[domain][risk]

    pattern = re.compile(
        r"{race\d*}|{religion\d*}|{colour\d*}|{nationality\d*}|"
        r"{sexual_orientation\d*}|{gender_identity\d*}|{disability\d*}"
        r"|{marital_status\d*}|{third_party\d*}|{financial_fraud\d*}|{ip_theft\d*}|"
        r"{income_level\d*}|{geography\d*}|{law_areas\d*}"
    )

    formatted_prompts = []
    for _idx, template in enumerate(templates):
        occurrences = pattern.findall(template)
        if len(occurrences) == 0:
            formatted_prompts.append(template)
            continue

        # TODO(Ananya): Combine into single logic
        if risk == "representation_gaps":
            combos: Optional[product[tuple[Any]] | permutations[tuple[Any]] | None] = (
                None
            )
            unique_occurrences = set(occurrences)
            keys = [re.sub("[{}]", "", key) for key in unique_occurrences]
            criterion = [
                legal[re.sub("[{}0-9]", "", key)] for key in unique_occurrences
            ]
            if len(criterion) == 1:
                combos = itertools.permutations(criterion[0], len(unique_occurrences))
            else:
                combos = itertools.product(*criterion)
            try:
                for combo in combos:
                    formatted_prompt = template
                    formatted_prompt = formatted_prompt.format(**dict(zip(keys, combo)))
                    formatted_prompts.append(formatted_prompt)
            except Exception as e:
                print(e)
        else:
            criterion = legal[re.sub("[{}]", "", occurrences[0])]
            for criteria in criterion:
                formatted_prompt = template.replace(occurrences[0], criteria)
                formatted_prompts.append(formatted_prompt)
    return formatted_prompts


def generate_prompts_healthcare(domain: str, risk: str) -> List[str]:
    """Generate user prompts for healthcare domain."""
    templates = user_prompt_templates[domain][risk]

    pattern = re.compile(
        r"{gender\d*}|{race\d*}|{sexual_identity\d*}|{age\d*}|{ses\d*}|{geographic_location\d*}|{ableism\d*}"
    )

    formatted_prompts = []
    for _idx, template in enumerate(templates):
        occurrences = pattern.findall(template)
        if len(occurrences) == 0:
            formatted_prompts.append(template)
            continue

        keys = [re.sub("[{}]", "", key) for key in set(occurrences)]
        criterion = {re.sub("[{}0-9]", "", val) for val in occurrences}
        criterion = set(criterion)
        criterion_vals = [healthcare[cri] for cri in criterion]
        if len(criterion) == 1:
            if (
                len(keys) == 1
            ):  # If {gender} occurs once, we want to keep the same value
                combos = criterion_vals[0]
            else:  # If {gender1}, {gender2} occur, we want permutations
                combos = itertools.permutations(criterion_vals[0], r=len(keys))
        else:  # multiple criteria
            combos = itertools.product(
                *criterion_vals, repeat=1
            )  # need product to combine

        try:
            for combo in combos:
                formatted_prompt = template
                if isinstance(combo, str):
                    formatted_prompt = formatted_prompt.format(**{keys[0]: combo})
                else:
                    formatted_prompt = formatted_prompt.format(**dict(zip(keys, combo)))
                formatted_prompts.append(formatted_prompt)
        except Exception as e:
            print(e)
    return formatted_prompts
