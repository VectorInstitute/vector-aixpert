"""Schema definitions OpenAI API response."""

from typing import List

from pydantic import BaseModel, ConfigDict, Field


class Candidate(BaseModel):
    """Candidate Schema for hiring scenes."""

    name: str
    age: int
    race: str
    gender: str
    SES: str
    model_config = ConfigDict(json_schema_extra={"additionalProperties": False})


class Scene(BaseModel):
    """Scene Schema for hiring scenes."""

    model_config = ConfigDict(json_schema_extra={"additionalProperties": False})
    text: str
    candidates: List[Candidate]


class MCQ(BaseModel):
    """Multiple Choice Question Schema."""

    model_config = ConfigDict(json_schema_extra={"additionalProperties": False})
    MCQ: str
    A: str
    B: str
    C: str
    D: str
    answer: str = Field(pattern="^[A-D]$", description="Correct option (A, B, C, or D)")
    explanation: str


class ToxicMCQ(BaseModel):
    """Toxicity Multiple Choice Question Schema."""

    model_config = ConfigDict(json_schema_extra={"additionalProperties": False})
    MCQ: str
    answer: str = Field(
        pattern="Yes|No|Unsure", description="Correct option (Yes, No, or Unsure)"
    )
    explanation: str
    phrases: List[str] | None = Field(
        description="List of phrases that indicate toxicity in the scene"
    )


class RepGapMCQ(BaseModel):
    """Representation Gap Multiple Choice Question Schema."""

    model_config = ConfigDict(json_schema_extra={"additionalProperties": False})
    MCQ: str
    A: str = Field(pattern="Yes", description="Option A")
    B: str = Field(pattern="No", description="Option B")
    C: str = Field(pattern="Unsure", description="Option C")
    D: str = Field(description="Option D")
    answer: str = Field(pattern="A|B|C|D", description="Correct option (A, B, C, or D)")
    explanation: str
    underrepresented_groups: List[str] | None = Field(
        description="List of underrepresented groups mentioned in the scene"
    )
    phrases: List[str] | None = Field(
        description="List of phrases that indicate representation gaps in the scene"
    )
