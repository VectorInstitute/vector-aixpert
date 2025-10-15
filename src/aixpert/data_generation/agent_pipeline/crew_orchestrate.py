"""file for creating crew and running it."""

import json
import os
import re
from typing import Any, Union

from agent import create_prompt_agents_and_task
from crewai import Crew
from custom_llm import CustomLLM
from flows.image_generation_flow import GeminiImageGenerationFlow
from load_text_llm import load_text_llm
from utils import load_prompt, read_directory, var_to_dict_prompts


current_script_dir = os.path.dirname(os.path.abspath(__file__))
prompts_base_path = os.path.join(current_script_dir, "prompts")
base_image_folder = os.path.join(current_script_dir, "images")


def my_local_model(prompt: str, temperature: float = 0.7) -> str:
    """Return a dummy model for validation of the pipeline."""
    return f"[Generated with temp={temperature}] {prompt}"


llm = CustomLLM(my_local_model)


def prompt_generation_flow(llm: Any) -> Union[str, list, None]:
    """Flow for creating the prompts."""
    prompts_base_path = "./prompts/"
    prompts, prompts_vqa = var_to_dict_prompts()
    print(prompts)
    # exit()
    task_list = []
    prompt_names = []
    for prompt_name, prompt in prompts.items():
        llm = load_text_llm("gemini")
        # print(llm)
        task_list.append(
            create_prompt_agents_and_task(role="AI Assistant", goal=prompt, llm=llm)
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
        output_jsonl_path = prompts_base_path + prompt_names[idx] + "_gemini.jsonl"
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
    prompt_file_names = read_directory(prompts_base_path)
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
            flow = GeminiImageGenerationFlow(elem["image_prompt"], output_filename)
            flow.kickoff()


def crew_create_and_launch(task_list: list) -> None:
    """Create crew and launch."""
    crew = Crew(tasks=task_list, verbose=False)
    crew.kickoff()


if __name__ == "__main__":
    # result = prompt_generation_flow(llm)
    image_generation_flow("gemini")
    # print(len(result))
