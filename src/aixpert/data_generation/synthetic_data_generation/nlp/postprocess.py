"""Postprocess generated MCQs by cleaning strings and ensuring proper formats."""

import argparse
import json
import os
import re
from collections import OrderedDict
from typing import Any, List, Tuple


def get_all_json_files(path: str) -> List[str]:
    """Get all JSON files from a directory or a single JSON file.

    :param path: (str) Path to the directory or JSON file.
    :return: (List[str]) List of JSON file paths.
    """
    is_dir = os.path.isdir(path)
    if is_dir:
        files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(".json")]
    else:
        files = [os.path.abspath(path)]
    return files


def load_mcqs(path: str) -> Tuple[List[str], List[List[dict[Any, Any]]]] | List:
    """Load a JSON file and return its content.

    :param path: (str) Path to the JSON file/dir with JSON files.
    :return: (dict|List[dict]) Loaded JSON content.
    """

    def load_json(file_path: str) -> List[dict]:
        with open(file_path, "r") as fp:
            return json.load(fp)

    if not os.path.exists(path):
        return []

    files = get_all_json_files(path)

    data = []
    try:
        for file in files:
            print(f"Loading {file}...")
            data.append(load_json(file))
    except Exception as e:
        print(f"Error loading JSON file {file}: {e}")
    return files, data


def clean_string(text: str) -> str:
    """Remove whitespace and replacing unicode characters.

    :param text: (str) Input text string.
    :return: (str) Cleaned text string.
    """
    unicode_replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "...",
        "\u00e2\u0080\u0099": "’",
        "\u00e2\u0080\u009c": "“",
        "\u00e2\u0080\u009d": "”",
        "\u00e2\u0080\u0093": "–",
        "\u00e2\u0080\u0094": "—",
        "\u00e2\u0080\u00a6": "…",
        "\u00c3\u00b1": "ñ",
    }

    text = text.strip("\n").strip()
    for k, v in unicode_replacements.items():
        text = re.sub(k, r"{}".format(v), text)
    return text


def postprocess(mcqs: dict) -> List[OrderedDict[str, Any]]:
    """Postprocess MCQs by cleaning strings and ensuring proper formats.

    :param mcqs: (dict) List of MCQ dictionaries to be processed.
    :return: (dict) Processed MCQs.
    """
    result = []
    for _, mcq in enumerate(mcqs):
        processed_mcq: OrderedDict[str, Any] = OrderedDict()
        for key, value in mcq.items():
            if value is None:
                processed_mcq[key] = []
            elif isinstance(value, str):
                processed_mcq[key] = clean_string(value)
            elif isinstance(value, list):
                processed_mcq[key] = [
                    clean_string(v) if isinstance(v, str) else v for v in value
                ]
            else:
                processed_mcq[key] = value

        result.append(processed_mcq)

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data_path", type=str, required=True, help="Path to data folder/file"
    )
    parser.add_argument(
        "--output_path",
        type=str,
        default="processed",
        help="Directory path to save processed files",
    )

    args = parser.parse_args()
    files, data = load_mcqs(args.data_path)

    print(f"Loaded {len(data)} entries from {args.data_path}")

    os.makedirs(args.output_path, exist_ok=True)
    for file, mcqs in zip(files, data):
        processed_mcqs = postprocess(mcqs)

        with open(f"{args.output_path}/{file.split('/')[-1]}", "w") as fp:
            json.dump(processed_mcqs, fp, indent=4, ensure_ascii=False)
        print(f"Processed file saved to {args.output_path}")
