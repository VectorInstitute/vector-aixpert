"""File for Customllm module."""

from typing import Any, Optional, Union

from crewai import BaseLLM


# Example: wrapping a local model object
class CustomLLM(BaseLLM):  # type: ignore[misc]
    """Defines a custom llm class module."""

    def __init__(self, model: Any, temperature: Optional[float] = None) -> None:
        """Define the underlying model with parameters."""
        super().__init__(model="local-llm", temperature=temperature)
        self.model = model  # could be a HuggingFace pipeline, llama.cpp instance, etc.

    def call(
        self,
        messages: Union[str, list[dict[str, str]]],
        tools: Optional[list[dict]] = None,
        callbacks: Optional[list[Any]] = None,
        available_functions: Optional[dict[str, Any]] = None,
        from_task: Optional[str] = None,
        from_agent: Optional[str] = None,
    ) -> str:
        """Call the model."""
        # Convert to plain text prompt if needed
        if isinstance(messages, list):
            prompt = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
        else:
            prompt = messages

        # Call your local model directly
        return self.model(prompt, temperature=self.temperature)

    def supports_function_calling(self) -> bool:
        """Check if the function calling is supported."""
        return False  # change if your model supports tool/function calls

    def get_context_window_size(self) -> int:
        """Return context window size."""
        return 4096  # adjust for your model
