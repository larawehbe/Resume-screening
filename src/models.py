"""
Pydantic models used across the pipeline.

These classes are the contracts between modules. Every LLM call in this
project returns structured data shaped like one of these models — that's
how we guarantee the agent's output is valid JSON with the right fields
instead of free-form text we'd have to parse ourselves.

When Claude is asked to "call the record_candidate tool", we hand it a
JSON schema generated from CandidateProfile. Claude's response must match
that schema. Pydantic then validates it on our side.
"""

from typing import Literal

from pydantic import BaseModel, Field


class Role(BaseModel):
    title: str
    company: str
    duration_months: int = Field(
        ge=0,
        description="Total time in the role, in months. Zero if unknown.",
    )
    description: str


class CandidateProfile(BaseModel):
    name: str
    years_experience: float = Field(
        ge=0,
        description="Total professional experience in years. May be fractional.",
    )
    skills: list[str]
    past_roles: list[Role]
    education: list[str]
    raw_summary: str = Field(
        description="One-paragraph summary of the candidate in their own words.",
    )


class DimensionScore(BaseModel):
    score: int = Field(ge=0, le=100)
    reasoning: str


class Gap(BaseModel):
    category: Literal["skill", "experience", "other"]
    detail: str


class ScoreReport(BaseModel):
    """What the scorer LLM returns. The orchestrator wraps this into a ScoredCandidate."""

    skills_match: DimensionScore
    experience_match: DimensionScore
    role_relevance: DimensionScore
    overall_fit: DimensionScore
    reasoning: str = Field(
        description="Two-sentence overall reasoning for the scores.",
    )
    gaps: list[Gap]


class ScoredCandidate(BaseModel):
    profile: CandidateProfile
    skills_match: DimensionScore
    experience_match: DimensionScore
    role_relevance: DimensionScore
    overall_fit: DimensionScore
    reasoning: str
    gaps: list[Gap]
    source_file: str


class CritiqueReport(BaseModel):
    """A second-pass review of a ScoreReport — used by the self-critique flow."""

    did_revise: bool = Field(
        description="True if the critic changed at least one score.",
    )
    critique: str = Field(
        description="One or two sentences explaining the critic's decision.",
    )
    revised_scores: ScoreReport


class ProcessingError(BaseModel):
    """Emitted when a resume fails at any stage. Keeps bad PDFs from crashing the run."""

    source_file: str
    stage: Literal["parse", "extract", "score"]
    message: str
