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


def create_metadata_agent(role: str, goal: str, llm: str) -> Agent:
    """Create metadata agent."""
    return Agent(
        role=role,  # stays the same
        goal=goal,  # changes each run
        backstory="",
        llm=llm,
        verbose=True,
    )


def create_metadata_tasks(metadata_agent: Agent, description: str) -> Task:
    """Create Associated Metadata Task."""
    return Task(
        description=description,
        agent=metadata_agent,
        expected_output="Give a correct response",
    )
