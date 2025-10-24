"""Schema definitions for OpenAI API response."""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class Candidate(BaseModel):
    """Candidate Schema for hiring scenes."""

    name: str
    age: int
    race: str
    gender: str
    SES: str
    model_config = ConfigDict(json_schema_extra={"additionalProperties": False})


class HiringScene(BaseModel):
    """Hiring Scene Schema for hiring scenes."""

    model_config = ConfigDict(json_schema_extra={"additionalProperties": False})
    text: str
    candidates: List[Candidate]


class Scene(BaseModel):
    """Scene Schema for hiring scenes."""

    model_config = ConfigDict(json_schema_extra={"additionalProperties": False})
    text: str


class MCQ(BaseModel):
    """Multiple Choice Question Schema."""

    model_config = ConfigDict(json_schema_extra={"additionalProperties": False})
    MCQ: str
    A: str
    B: str
    C: str
    D: str


class BiasAnswer(BaseModel):
    """Bias Answer Schema."""

    model_config = ConfigDict(json_schema_extra={"additionalProperties": False})
    answer: str = Field(pattern="^[A-D]$", description="Correct option (A, B, C, or D)")
    explanation: str
    criteria: Optional[List[str] | None] = Field(
        description="List of criteria relevant to bias in the scene"
    )


class ToxicityAnswer(BaseModel):
    """Toxicity Answer Schema."""

    model_config = ConfigDict(json_schema_extra={"additionalProperties": False})
    answer: str = Field(
        pattern="^[A-E]$", description="Correct option (A, B, C, D, or E)"
    )
    explanation: str
    phrases: List[str] | None = Field(
        description="List of phrases that indicate toxicity in the scene"
    )


class RepGapAnswer(BaseModel):
    """Representation Gap Answer Schema."""

    model_config = ConfigDict(json_schema_extra={"additionalProperties": False})
    answer: str = Field(pattern="^[A-C]$", description="Correct option (A, B, or C)")
    explanation: str
    underrepresented_groups: List[str] | None = Field(
        description="List of underrepresented groups mentioned in the scene"
    )
    phrases: List[str] | None = Field(
        description="List of phrases that indicate representation gaps in the scene"
    )


class SecurityRiskAnswer(BaseModel):
    """Security Risk Answer Schema."""

    model_config = ConfigDict(json_schema_extra={"additionalProperties": False})
    answer: str = Field(pattern="^[A-C]$", description="Correct option (A, B, or C)")
    explanation: str
    risk_type: List[str] | None = Field(
        description="Type(s) of security risks mentioned in the scene"
    )
    risk_indicators: List[str] | None = Field(
        description="List of phrases from the scenario that indicate the security risk"
    )


# Schema utility functions
def get_scene_schema(domain: str) -> Optional[dict]:
    """Get the JSON schema for scene generation.

    :param domain: (str) The domain of the scene (e.g., "hiring").
    :return: (dict) The JSON schema for the specified domain.
    """
    if domain == "hiring":
        return HiringScene.model_json_schema()

    return Scene.model_json_schema()


def get_mcq_schema(risk: str) -> Optional[dict]:
    """Get the JSON schema for MCQ generation.

    :param risk: (str) The type of risk (e.g., "bias_discrimination")
    :return: (dict) The JSON schema for the specified risk type.
    """
    if risk == "bias_discrimination":
        return MCQ.model_json_schema()

    return None


def get_answer_schema(risk: str) -> Optional[dict]:
    """Get the JSON schema for answer generation.

    :param risk: (str) The type of risk (e.g., "bias_discrimination")
    :return: (dict) The JSON schema for the specified risk type.
    """
    if risk == "bias_discrimination":
        return BiasAnswer.model_json_schema()
    if risk == "toxicity":
        return ToxicityAnswer.model_json_schema()
    if risk == "representation_gaps":
        return RepGapAnswer.model_json_schema()
    if risk == "security_risks":
        return SecurityRiskAnswer.model_json_schema()

    return None
