"""Tests for extractor.py — mocks the Anthropic client, no real API calls."""

from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from src.extractor import EXTRACTION_TOOL_NAME, extract_candidate
from src.models import CandidateProfile
from src.prompts import EXTRACTION_SYSTEM_PROMPT


# Builds a fake Anthropic response. The real response has `.content` (a list
# of blocks) where each block has `.type` and, for tool_use blocks, `.input`.
# MagicMock lets us fake that shape without importing the real Anthropic types.
def _fake_response(tool_input: dict) -> MagicMock:
    block = MagicMock(type="tool_use", input=tool_input)
    response = MagicMock()
    response.content = [block]
    return response


_VALID_INPUT = {
    "name": "Alice Chen",
    "years_experience": 5.0,
    "skills": ["Python", "SQL"],
    "past_roles": [
        {
            "title": "Backend Engineer",
            "company": "Acme",
            "duration_months": 24,
            "description": "Worked on APIs.",
        }
    ],
    "education": ["BS Computer Science"],
    "raw_summary": "I build backend systems.",
}


def test_extract_candidate_returns_validated_profile() -> None:
    client = MagicMock()
    client.messages.create.return_value = _fake_response(_VALID_INPUT)

    profile = extract_candidate(client, resume_text="anything")

    assert isinstance(profile, CandidateProfile)
    assert profile.name == "Alice Chen"
    assert profile.skills == ["Python", "SQL"]


def test_extract_candidate_sends_correct_request() -> None:
    client = MagicMock()
    client.messages.create.return_value = _fake_response(_VALID_INPUT)

    extract_candidate(client, resume_text="RESUME TEXT", model="claude-test-model")

    # call_args.kwargs is the dict of keyword arguments the function passed in.
    kwargs = client.messages.create.call_args.kwargs
    assert kwargs["model"] == "claude-test-model"
    assert kwargs["max_tokens"] == 4096
    assert kwargs["system"] == EXTRACTION_SYSTEM_PROMPT
    assert kwargs["tool_choice"] == {"type": "tool", "name": EXTRACTION_TOOL_NAME}
    assert kwargs["tools"][0]["name"] == EXTRACTION_TOOL_NAME
    assert kwargs["tools"][0]["input_schema"] == CandidateProfile.model_json_schema()
    assert kwargs["messages"] == [{"role": "user", "content": "RESUME TEXT"}]


def test_extract_candidate_raises_when_llm_returns_invalid_data() -> None:
    bad_input = {"name": "Alice"}  # missing required fields
    client = MagicMock()
    client.messages.create.return_value = _fake_response(bad_input)

    with pytest.raises(ValidationError):
        extract_candidate(client, resume_text="anything")
