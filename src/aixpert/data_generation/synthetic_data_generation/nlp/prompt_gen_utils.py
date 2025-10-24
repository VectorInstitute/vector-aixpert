"""Generate user prompts based on templates and demographics."""

import itertools
import re
from typing import Any, Iterable, List, Tuple

from prompt_template import demographics, healthcare, legal, user_prompt_templates


# TODO: Combine into single function with domain as argument (IF POSSIBLE)
# TODO: Replace permutations with combinations everywhere to reduce duplicate prompt
def generate_prompts_hiring(domain: str, risk: str) -> List[str]:
    """
    Generate user prompts for hiring domain.

    :param domain: (str) Domain name.
    :param risk: (str) Risk type.
    :return: (List[str]) List of formatted user prompts.
    """
    templates = user_prompt_templates[domain][risk]
    pattern = re.compile(
        r"{gender\d*}|{age\d*}|{race\d*}|{ses\d*}|{work_place\d*}|{disability\d*}|{tech_experience\d*}|{location\d*}|{policy_awareness\d*}"
    )

    formatted_prompts = []
    for _, template in enumerate(templates):
        # Find all occurrences of the demographic placeholders
        occurrences = pattern.findall(template)
        if len(occurrences) == 0:
            formatted_prompts.append(template)
            continue

        # Has only one demographic type to substitute. e.g. {gender}
        demographic = demographics[re.sub("[{}0-9]", "", occurrences[0])]
        # Create permutations of demographic values to fill in the placeholders
        combos = itertools.permutations(demographic, len(set(occurrences)))

        # Format prompts
        for combo in combos:
            formatted_prompt = template
            for i in range(len(combo)):
                formatted_prompt = formatted_prompt.replace(occurrences[i], combo[i])
            formatted_prompts.append(formatted_prompt)

    return formatted_prompts


def generate_prompts_legal(domain: str, risk: str) -> List[str]:
    """
    Generate user prompts for legal domain.

    :param domain: (str) Domain name.
    :param risk: (str) Risk type.
    :return: (List[str]) List of formatted user prompts.
    """
    templates = user_prompt_templates[domain][risk]
    pattern = re.compile(
        r"{race\d*}|{religion\d*}|{colour\d*}|{nationality\d*}|"
        r"{sexual_orientation\d*}|{gender_identity\d*}|{disability\d*}"
        r"|{marital_status\d*}|{third_party\d*}|{financial_fraud\d*}|{ip_theft\d*}|{income_level\d*}|{geography\d*}|{law_areas\d*}"
    )

    formatted_prompts = []
    for _idx, template in enumerate(templates):
        # Find all occurrences of the demographic placeholders
        occurrences = pattern.findall(template)
        if len(occurrences) == 0:
            formatted_prompts.append(template)
            continue

        # TODO(Ananya): Combine into single logic
        if risk == "representation_gaps":
            unique_occurrences = set(occurrences)
            # Get all the demographic  keys in the template. Eg. race1, race2
            keys = [re.sub("[{}]", "", key) for key in unique_occurrences]

            # Get values for all the unique demographic types in the template.
            criterion = [
                legal[re.sub("[{}0-9]", "", key)] for key in unique_occurrences
            ]

            combos: Iterable[Tuple[Any, ...]]
            # Get permutations of the values of single demographic type.
            if len(criterion) == 1:
                combos = itertools.permutations(criterion[0], len(unique_occurrences))
            else:
                combos = itertools.product(
                    *criterion
                )  # Get combinations of different demographic types

            # Get formatted prompts by substituting demographic values in the template
            try:
                for combo in combos:
                    formatted_prompt = template
                    formatted_prompt = formatted_prompt.format(**dict(zip(keys, combo)))
                    formatted_prompts.append(formatted_prompt)
            except Exception as e:
                print(e)
        else:
            # Get values for single demographic type in the template
            criterion = legal[re.sub("[{}]", "", occurrences[0])]
            for criteria in criterion:
                formatted_prompt = template.replace(occurrences[0], criteria)
                formatted_prompts.append(formatted_prompt)
    return formatted_prompts


def generate_prompts_healthcare(domain: str, risk: str) -> List[str]:
    """
    Generate user prompts for healthcare domain.

    :param domain: (str) Domain name.
    :param risk: (str) Risk type.
    :return: (List[str]) List of formatted user prompts.
    """
    templates = user_prompt_templates[domain][risk]

    pattern = re.compile(
        r"{gender\d*}|{race\d*}|{sexual_identity\d*}|{age\d*}|{ses\d*}|{geographic_location\d*}|{ableism\d*}"
    )

    formatted_prompts = []
    for _idx, template in enumerate(templates):
        # Find all occurrences of the demographic placeholders
        occurrences = pattern.findall(template)
        if len(occurrences) == 0:
            formatted_prompts.append(template)
            continue

        # Get all demographic for template substitution. Eg. race1, race2
        keys = [re.sub("[{}]", "", key) for key in set(occurrences)]

        # Get all demographic occurrences. e.g. race if race1 and race2 occur
        criterion: set[str] = {re.sub("[{}0-9]", "", val) for val in occurrences}

        # Get set of demographic values
        criterion = set(criterion)

        # Get list of lists of demographic values
        criterion_vals: List[List[str]] = [healthcare[cri] for cri in criterion]

        combos: Iterable[Tuple[Any, ...]]
        if len(criterion) == 1:
            if (
                len(keys) == 1
            ):  # If {gender} occurs once, we want to keep the same value
                combos = [(val,) for val in criterion_vals[0]]

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
                    # If only 1 demographic placeholder repeated multiple times
                    formatted_prompt = formatted_prompt.format(**{keys[0]: combo})
                else:
                    # If multiple different demographic placeholders
                    formatted_prompt = formatted_prompt.format(**dict(zip(keys, combo)))
                formatted_prompts.append(formatted_prompt)
        except Exception as e:
            print(e)
    return formatted_prompts


def run_prompt_generation(domain: str, risk: str) -> List[str]:
    """
    Generate user prompts for a domain and risk type.

    :param domain: (str) Domain name.
    :param risk: (str) Risk type.
    :return: (List[str]) List of formatted user prompts.
    """
    if domain == "hiring":
        user_prompts = generate_prompts_hiring(domain, risk)
    elif domain == "legal":
        user_prompts = generate_prompts_legal(domain, risk)
    elif domain == "healthcare":
        user_prompts = generate_prompts_healthcare(domain, risk)

    return user_prompts
