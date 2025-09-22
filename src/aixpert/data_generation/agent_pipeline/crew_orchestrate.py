"""file for creating crew and running it."""

from typing import Any, Union

from agent import create_prompt_agents_and_task
from crewai import Crew
from custom_llm import CustomLLM
from utils import var_to_dict_prompts


def my_local_model(prompt: str, temperature: float = 0.7) -> str:
    """Return a dummy model for validation of the pipeline."""
    return f"[Generated with temp={temperature}] {prompt}"


llm = CustomLLM(my_local_model)


def prompt_generation_flow(llm: Any) -> Union[str, list, None]:
    """Flow for creating the prompts."""
    prompts, prompts_vqa = var_to_dict_prompts()
    task_list = []
    for _prompt_name, prompt in prompts.items():
        task_list.append(
            create_prompt_agents_and_task(role="AI Assistant", goal=prompt, llm=llm)
        )
    crew_create_and_launch(task_list)
    for task in task_list:
        if isinstance(task.output.raw, list):
            prompts = [p.strip() for p in task.output.raw if p]
        else:
            prompts = [task.output.raw.strip()] if task.output.raw else []
    return prompts if len(prompts) > 1 else (prompts[0] if prompts else None)


def crew_create_and_launch(task_list: list) -> None:
    """Create crew and launch."""
    crew = Crew(tasks=task_list, verbose=True)
    crew.kickoff()


if __name__ == "__main__":
    result = prompt_generation_flow(llm)
    # print("\n=== FINAL RESULT ===")
    print(type(result))
    # print(len(result))
