"""
First LLM call: turn raw resume text into a CandidateProfile.

This file shows Claude's tool use pattern for structured output:
1. Define a "tool" whose input_schema is the JSON schema of our Pydantic model.
2. Force Claude to call that tool via `tool_choice`.
3. Pull the tool_use block out of the response and validate with Pydantic.

The exact same pattern appears in scorer.py and critique.py. Once you
recognise it here, the others read the same way.
"""

from anthropic import Anthropic

from src.models import CandidateProfile
from src.prompts import EXTRACTION_SYSTEM_PROMPT

DEFAULT_MODEL = "claude-sonnet-4-6"
EXTRACTION_TOOL_NAME = "record_candidate"


def extract_candidate(
    client: Anthropic,
    resume_text: str,
    model: str = DEFAULT_MODEL,
) -> CandidateProfile:
    """Extract a structured candidate profile from raw resume text."""

    # The tool definition. input_schema is the JSON Schema of our Pydantic
    # model, so Claude knows exactly which fields to produce.
    tool = {
        "name": EXTRACTION_TOOL_NAME,
        "description": "Record a structured summary of the candidate described in the resume.",
        "input_schema": CandidateProfile.model_json_schema(),
    }

    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=EXTRACTION_SYSTEM_PROMPT,
        tools=[tool],
        # Force Claude to call our tool — no free-form text answer allowed.
        tool_choice={"type": "tool", "name": EXTRACTION_TOOL_NAME},
        messages=[{"role": "user", "content": resume_text}],
    )

    # The response is a list of content blocks. With forced tool_choice,
    # we expect exactly one block of type "tool_use".
    # Find the tool_use block in the response
    tool_use = None
    for block in response.content:
        if block.type == "tool_use":
            tool_use = block
            break

    # Pydantic validates Claude's JSON matches our schema and turns it into
    # a typed Python object.
    return CandidateProfile.model_validate(tool_use.input)
