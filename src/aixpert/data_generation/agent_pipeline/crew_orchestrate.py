"""file for creating crew and running it."""

import argparse
import json
import os
import re
from typing import Any, Union

from agent import (
    create_metadata_agent,
    create_metadata_tasks,
    create_prompt_agents_and_task,
)
from crewai import Crew
from custom_llm import CustomLLM
from flows.image_generation_flow import ImageGenerationFlow
from flows.vqa_generation_flow import VQAGenerationFlow
from load_text_llm import load_text_llm
from utils import check_last_index, load_prompt, read_directory, var_to_dict_prompts


current_script_dir = os.path.dirname(os.path.abspath(__file__))
prompts_base_path = os.path.join(current_script_dir, "prompts")
base_image_folder = os.path.join(current_script_dir, "images")
metadata_base_path = os.path.join(current_script_dir, "metadata")
vqa_base_path = os.path.join(current_script_dir, "vqa")


def my_local_model(prompt: str, temperature: float = 0.7) -> str:
    """Return a dummy model for validation of the pipeline."""
    return f"[Generated with temp={temperature}] {prompt}"


llm = CustomLLM(my_local_model)


def prompt_generation_flow(llm: Any) -> Union[str, list, None]:
    """Flow for creating the prompts."""
    prompts, prompts_vqa, prompt_metadata = var_to_dict_prompts()
    # print(prompts)
    # exit()
    task_list = []
    prompt_names = []
    for prompt_name, prompt in prompts.items():
        llm_model = load_text_llm(llm)
        # print(llm)
        task_list.append(
            create_prompt_agents_and_task(
                role="AI Assistant", goal=prompt, llm=llm_model
            )
        )
        prompt_names.append(prompt_name)
    # print(prompt_names)
    crew_create_and_launch(task_list)
    # print(task_list[0].output.raw)
    # print(len(task_list))
    for idx, task in enumerate(task_list):
        if isinstance(task.output.raw, list):
            prompts = [p.strip() for p in task.output.raw if p]
        else:
            prompts = [task.output.raw.strip()] if task.output.raw else []
        content = "\n".join(prompts) if isinstance(prompts, list) else prompts
        json_objects = re.findall(r"```json(.*)```", content, re.DOTALL)
        os.makedirs(prompts_base_path, exist_ok=True)
        prompts_llm_path = os.path.join(prompts_base_path, llm)
        os.makedirs(prompts_llm_path, exist_ok=True)
        output_jsonl_path = os.path.join(prompts_llm_path, prompt_names[idx] + ".json")
        with open(output_jsonl_path, "w", encoding="utf-8") as f:
            for obj_str in json_objects:
                try:
                    obj = json.loads(obj_str)
                    json_line = json.dumps(obj, ensure_ascii=False)
                    f.write(json_line + "\n")
                except json.JSONDecodeError as e:
                    print(f"Skipping invalid JSON: {e}")

    print("Prompts generation completed successfully.")
    return prompts if len(prompts) > 1 else (prompts[0] if prompts else None)


def image_generation_flow(llm: str) -> None:
    """Flow for creating the images from the prompt."""
    prompts_llm_path = os.path.join(prompts_base_path, llm)
    prompt_file_names = read_directory(prompts_llm_path)
    os.makedirs(base_image_folder, exist_ok=True)
    for file in prompt_file_names:
        # print(file)
        prompts = load_prompt(file)
        print(len(prompts))
        for i, elem in enumerate(prompts):
            domain = elem["domain"]
            risk = elem["risk"]
            output_filename = f"{domain}_{risk}_image_{i + 1}.png"
            image_folder = os.path.join(base_image_folder, llm)
            os.makedirs(image_folder, exist_ok=True)
            folder_name = os.path.join(image_folder, f"{domain}_{risk}_images")
            os.makedirs(folder_name, exist_ok=True)
            print(f"Saving image to folder: {folder_name}")
            output_filename = f"{domain}_{risk}_image_{i + 1}.png"
            output_filename = os.path.join(folder_name, output_filename)
            if os.path.exists(output_filename):
                print("file exist so skipping")
                continue
            flow = ImageGenerationFlow(llm, elem["image_prompt"], output_filename)
            flow.kickoff()


def metadata_generation_pipeline(llm: Any) -> None:
    """Pipeline for creating the metadata from the prompt."""
    prompts, prompts_vqa, prompt_metadata = var_to_dict_prompts()
    prompts_llm_path = os.path.join(prompts_base_path, llm)
    prompt_file_names = read_directory(prompts_llm_path)
    # for prompt_name, prompt in prompts_metadata.items():
    llm_model = load_text_llm(llm)
    metadata_agent = create_metadata_agent(
        role="AI Assistant", goal=prompt_metadata["prompt_metadata"], llm=llm_model
    )
    for file in prompt_file_names:
        # print(file)
        prompts = load_prompt(file)
        # print(len(prompts))
        for i, elem in enumerate(prompts):
            task_list = []
            domain = elem["domain"]
            risk = elem["risk"]
            task_list.append(
                create_metadata_tasks(metadata_agent, elem["image_prompt"])
            )
            crew_create_and_launch(task_list)
            for _idx, task in enumerate(task_list):
                if isinstance(task.output.raw, list):
                    prompts = [p.strip() for p in task.output.raw if p]
                else:
                    prompts = [task.output.raw.strip()] if task.output.raw else []
            content = "\n".join(prompts) if isinstance(prompts, list) else prompts
            metadata = re.findall(r"```json(.*)```", content, re.DOTALL)
            if len(metadata) != 1:
                metadata = [content]
            assert len(metadata) == 1, "there should be only one metadata generated"
            try:
                metadata = json.loads(metadata[0])
            except json.JSONDecodeError as e:
                print(f"Skipping invalid JSON for entry {i} : {e}")
                continue
            output_filename = f"{domain}_{risk}_image_{i + 1}.png"
            image_folder = os.path.join(base_image_folder, llm)
            folder_name = os.path.join(image_folder, f"{domain}_{risk}_images")
            output_filename = f"{domain}_{risk}_image_{i + 1}.png"
            # output_filename = os.path.join(folder_name, output_filename)
            output_filename_path = os.path.join(folder_name, output_filename)
            if not os.path.exists(output_filename_path):
                print("image file doesn't exist so skipping")
                continue
            os.makedirs(metadata_base_path, exist_ok=True)
            metadata_llm_path = os.path.join(metadata_base_path, llm)
            os.makedirs(metadata_llm_path, exist_ok=True)
            output_jsonl_path = os.path.join(
                metadata_llm_path,
                elem["domain"] + "_" + elem["risk"] + "_metadata.jsonl",
            )
            parsed = {
                "domain": elem["domain"],
                "risk": elem["risk"],
                "image_prompt": elem["image_prompt"],
                "image_path": output_filename_path,
                "metadata": metadata["metadata"],
            }
            with open(output_jsonl_path, "a", encoding="utf-8") as f:
                json_line = json.dumps(parsed, ensure_ascii=False)
                f.write(json_line + "\n")
            print("Metadata saved successfully.")


def vqa_generation_pipeline(llm: Any) -> None:
    """Pipeline for creating the vqa from the image."""
    prompts, prompts_vqa, prompt_metadata = var_to_dict_prompts()
    metadata_llm_path = os.path.join(metadata_base_path, llm)
    metadata_file_names = read_directory(metadata_llm_path)
    for prompt_name, prompt in prompts_vqa.items():
        for file in metadata_file_names:
            prompts = load_prompt(file)
            # print(len(prompts))
            for i, elem in enumerate(prompts):
                # domain = elem["domain"]
                # risk = elem["risk"]
                # image_path = elem["image_path"]
                # image_prompt = elem["image_prompt"]
                os.makedirs(metadata_base_path, exist_ok=True)
                vqa_llm_path = os.path.join(vqa_base_path, llm)
                os.makedirs(vqa_llm_path, exist_ok=True)
                vqa_type_path = os.path.join(vqa_llm_path, prompt_name)
                os.makedirs(vqa_type_path, exist_ok=True)
                output_jsonl_path = os.path.join(
                    vqa_type_path,
                    elem["domain"] + "_" + elem["risk"] + "_vqa.jsonl",
                )
                parsed = {
                    "domain": elem["domain"],
                    "risk": elem["risk"],
                    "image_prompt": elem["image_prompt"],
                    "image_path": elem["image_path"],
                    "metadata": elem["metadata"],
                }
                print(output_jsonl_path)
                index = check_last_index(output_jsonl_path)
                if i < index:
                    continue
                flow = VQAGenerationFlow(llm, prompt, output_jsonl_path, parsed)
                # flow = GeminiImageGenerationFlow("./","test.png")
                # flow.plot()
                flow.kickoff()


def crew_create_and_launch(task_list: list) -> None:
    """Create crew and launch."""
    crew = Crew(tasks=task_list, verbose=False)
    crew.kickoff()


def get_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Agentic Pipeline")
    parser.add_argument(
        "--llm",
        type=str,
        required=True,
        help="llm to be used, Supported Models [Openai, Gemini]",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = get_arguments()
    if args.llm not in ["openai", "gemini"]:
        raise ValueError("Supported models are Openai and Gemini only ")
    prompt_generation_flow(args.llm)
    image_generation_flow(args.llm)
    metadata_generation_pipeline(args.llm)
    vqa_generation_pipeline(args.llm)
    # print(len(result))
