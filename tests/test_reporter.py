"""Tests for reporter.py — pure transform, no API calls."""

import json
from pathlib import Path

from src.models import (
    CandidateProfile,
    DimensionScore,
    Gap,
    ProcessingError,
    Role,
    ScoredCandidate,
)
from src.reporter import write_json, write_markdown


def _make_scored(name: str, overall: int, source: str) -> ScoredCandidate:
    return ScoredCandidate(
        profile=CandidateProfile(
            name=name,
            years_experience=5.0,
            skills=["Python", "SQL"],
            past_roles=[
                Role(
                    title="Backend Engineer",
                    company="Acme",
                    duration_months=24,
                    description="Worked on APIs.",
                )
            ],
            education=["BS Computer Science"],
            raw_summary="I build backend systems.",
        ),
        skills_match=DimensionScore(score=overall - 5, reasoning="Skills reason"),
        experience_match=DimensionScore(score=overall, reasoning="Experience reason"),
        role_relevance=DimensionScore(score=overall + 2, reasoning="Role reason"),
        overall_fit=DimensionScore(score=overall, reasoning="Overall reason"),
        reasoning="Two-sentence reasoning. Looks strong.",
        gaps=[Gap(category="skill", detail="No Kafka experience")],
        source_file=source,
    )


def test_json_output_sorts_by_overall_fit(tmp_path: Path) -> None:
    results = [
        _make_scored("Bob", 70, "bob.pdf"),
        _make_scored("Alice", 90, "alice.pdf"),
        _make_scored("Carol", 80, "carol.pdf"),
    ]

    out = tmp_path / "results.json"
    write_json(results, out)

    data = json.loads(out.read_text())
    names = [c["profile"]["name"] for c in data["candidates"]]
    assert names == ["Alice", "Carol", "Bob"]
    assert data["errors"] == []


def test_json_separates_errors_from_candidates(tmp_path: Path) -> None:
    results = [
        _make_scored("Alice", 90, "alice.pdf"),
        ProcessingError(
            source_file="broken.pdf", stage="parse", message="PDF corrupt"
        ),
    ]

    out = tmp_path / "results.json"
    write_json(results, out)

    data = json.loads(out.read_text())
    assert len(data["candidates"]) == 1
    assert data["candidates"][0]["profile"]["name"] == "Alice"
    assert len(data["errors"]) == 1
    assert data["errors"][0]["stage"] == "parse"


def test_markdown_contains_ranked_table_and_sections(tmp_path: Path) -> None:
    results = [
        _make_scored("Bob", 70, "bob.pdf"),
        _make_scored("Alice", 90, "alice.pdf"),
    ]

    out = tmp_path / "report.md"
    write_markdown(results, out, Path("jd.txt"))
    content = out.read_text()

    assert "# Resume Match Report" in content
    assert "## Ranked candidates" in content
    assert "Alice" in content
    assert "Bob" in content
    # Alice should appear before Bob in the ranked table
    assert content.index("Alice") < content.index("Bob")


def test_markdown_includes_error_section_when_errors_present(tmp_path: Path) -> None:
    results = [
        _make_scored("Alice", 90, "alice.pdf"),
        ProcessingError(
            source_file="broken.pdf", stage="extract", message="API timeout"
        ),
    ]

    out = tmp_path / "report.md"
    write_markdown(results, out, Path("jd.txt"))
    content = out.read_text()

    assert "## Could not process" in content
    assert "broken.pdf" in content
    assert "extract" in content
    assert "API timeout" in content


def test_markdown_omits_error_section_when_no_errors(tmp_path: Path) -> None:
    results = [_make_scored("Alice", 90, "alice.pdf")]

    out = tmp_path / "report.md"
    write_markdown(results, out, Path("jd.txt"))
    content = out.read_text()

    assert "## Could not process" not in content
