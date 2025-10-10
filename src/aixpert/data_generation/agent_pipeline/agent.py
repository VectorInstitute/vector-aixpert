"""File for definition of agent and task functions."""

from crewai import Agent, Task


def create_prompt_agents_and_task(role: str, goal: str, llm: str) -> Task:
    """Create prompt agents and tasks assoviated with them."""
    prompt_engineer = Agent(
        role=role,  # stays the same
        goal=goal,  # changes each run
        backstory="",
        llm=llm,
        verbose=True,
    )
    return Task(
        description="Generate 40 such examples that follow the guidelines in the system prompt and match the provided JSON output example.",
        agent=prompt_engineer,
        expected_output="Give a correct response",
    )


if __name__ == "__main__":
    main_prompt = "A futuristic city skyline at sunset with flying cars"
    # prompt_dict, prompt_vqa_dict = var_to_dict_prompts()
    # print(prompt_dict, prompt_vqa_dict)
    # create_prompt_agents_and_task(role="AI Assistant", goal="", llm=llm)
