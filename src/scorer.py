"""
Second LLM call: score a candidate against a job description.

Same tool use + Pydantic pattern as extractor.py. The one new technique
here is prompt caching: because every resume is scored against the same
JD, we mark the JD block as cacheable. After the first call, Claude
serves the JD tokens from cache at ~10% of the normal cost.

This file exposes two functions:

- `score_candidate`: one API call. The default.
- `score_candidate_ensemble`: call score_candidate N times, return the
  median score per dimension. Costs N× as much; useful for seeing how
  much per-call variance there is.
"""

from statistics import median

from anthropic import Anthropic

from src.models import (
    CandidateProfile,
    DimensionScore,
    ScoredCandidate,
    ScoreReport,
)
from src.prompts import SCORING_SYSTEM_PROMPT

DEFAULT_MODEL = "claude-sonnet-4-6"
SCORING_TOOL_NAME = "record_score"


def score_candidate(
    client: Anthropic,
    profile: CandidateProfile,
    jd: str,
    source_file: str,
    model: str = DEFAULT_MODEL,
) -> ScoredCandidate:
    """Score a candidate against a job description with a single API call."""

    tool = {
        "name": SCORING_TOOL_NAME,
        "description": "Record the score, reasoning, and gaps for this candidate against the JD.",
        "input_schema": ScoreReport.model_json_schema(),
    }

    profile_text = profile.model_dump_json(indent=2)

    # We send two pieces of content in the user message: the JD and the
    # candidate profile. The JD is identical for every resume in this run,
    # so we mark it with cache_control. After the first call Claude will
    # serve the JD portion from cache at ~0.1× the normal input cost.
    user_content = [
        {
            "type": "text",
            "text": f"<job_description>\n{jd}\n</job_description>",
            "cache_control": {"type": "ephemeral"},
        },
        {
            "type": "text",
            "text": f"<candidate_profile>\n{profile_text}\n</candidate_profile>",
        },
    ]

    response = client.messages.create(
        model=model,
        max_tokens=2048,
        system=SCORING_SYSTEM_PROMPT,
        tools=[tool],
        tool_choice={"type": "tool", "name": SCORING_TOOL_NAME},
        messages=[{"role": "user", "content": user_content}],
    )

    tool_use = next(block for block in response.content if block.type == "tool_use")
    report = ScoreReport.model_validate(tool_use.input)

    # The LLM only returned scores and reasoning. We attach the candidate
    # profile and source filename to build the full ScoredCandidate.
    return ScoredCandidate(
        profile=profile,
        source_file=source_file,
        skills_match=report.skills_match,
        experience_match=report.experience_match,
        role_relevance=report.role_relevance,
        overall_fit=report.overall_fit,
        reasoning=report.reasoning,
        gaps=report.gaps,
    )


def score_candidate_ensemble(
    client: Anthropic,
    profile: CandidateProfile,
    jd: str,
    source_file: str,
    n_samples: int,
    model: str = DEFAULT_MODEL,
) -> ScoredCandidate:
    """Call score_candidate N times and return per-dimension medians.

    Reasoning and gaps are taken from the first run — combining text across
    runs would create Frankenstein explanations. Using the first run keeps
    the output internally consistent.
    """
    if n_samples < 1:
        raise ValueError("n_samples must be at least 1")

    runs = [
        score_candidate(client, profile, jd, source_file, model)
        for _ in range(n_samples)
    ]
    first = runs[0]

    return ScoredCandidate(
        profile=first.profile,
        source_file=first.source_file,
        skills_match=DimensionScore(
            score=int(median(r.skills_match.score for r in runs)),
            reasoning=first.skills_match.reasoning,
        ),
        experience_match=DimensionScore(
            score=int(median(r.experience_match.score for r in runs)),
            reasoning=first.experience_match.reasoning,
        ),
        role_relevance=DimensionScore(
            score=int(median(r.role_relevance.score for r in runs)),
            reasoning=first.role_relevance.reasoning,
        ),
        overall_fit=DimensionScore(
            score=int(median(r.overall_fit.score for r in runs)),
            reasoning=first.overall_fit.reasoning,
        ),
        reasoning=first.reasoning,
        gaps=first.gaps,
    )
