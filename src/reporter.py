"""
Results -> JSON file + readable markdown report.

Pure functions: no I/O beyond writing the two files, no async, no API calls.
Easy to unit-test with hand-built ScoredCandidate lists.
"""

import json

from src.models import ProcessingError, ScoredCandidate

Result = ScoredCandidate | ProcessingError


def write_json(results: list[Result], path: str) -> None:
    ranked, errors = _split_and_sort(results)
    payload = {
        "candidates": [c.model_dump() for c in ranked],
        "errors": [e.model_dump() for e in errors],
    }
    with open(path, "w") as f:
        f.write(json.dumps(payload, indent=2))


def write_markdown(results: list[Result], path: str, jd_path: str) -> None:
    ranked, errors = _split_and_sort(results)
    lines: list[str] = []

    lines.append(f"# Resume Match Report")
    lines.append("")
    lines.append(f"_Job description: `{jd_path}`_")
    lines.append("")

    lines.append("## Ranked candidates")
    lines.append("")
    if ranked:
        lines.append("| Rank | Candidate | Overall | Skills | Experience | Role relevance |")
        lines.append("|------|-----------|---------|--------|------------|----------------|")
        for i, c in enumerate(ranked, 1):
            lines.append(
                f"| {i} | {c.profile.name} | {c.overall_fit.score} | "
                f"{c.skills_match.score} | {c.experience_match.score} | "
                f"{c.role_relevance.score} |"
            )
    else:
        lines.append("_No candidates were scored._")
    lines.append("")

    for c in ranked:
        lines.extend(_render_candidate_section(c))

    if errors:
        lines.append("## Could not process")
        lines.append("")
        for e in errors:
            lines.append(f"- **{e.source_file}** (failed at `{e.stage}`): {e.message}")
        lines.append("")

    with open(path, "w") as f:
        f.write("\n".join(lines))


def _split_and_sort(
    results: list[Result],
) -> tuple[list[ScoredCandidate], list[ProcessingError]]:
    ranked = sorted(
        (r for r in results if isinstance(r, ScoredCandidate)),
        key=lambda c: c.overall_fit.score,
        reverse=True,
    )
    errors = [r for r in results if isinstance(r, ProcessingError)]
    return ranked, errors


def _render_candidate_section(c: ScoredCandidate) -> list[str]:
    lines: list[str] = []
    lines.append(f"## {c.profile.name}  — {c.overall_fit.score}/100")
    lines.append("")
    lines.append(f"_Source: `{c.source_file}` · {c.profile.years_experience:.1f} years experience_")
    lines.append("")
    lines.append(c.reasoning)
    lines.append("")
    lines.append("### Scores")
    lines.append(f"- **Skills match** ({c.skills_match.score}): {c.skills_match.reasoning}")
    lines.append(f"- **Experience match** ({c.experience_match.score}): {c.experience_match.reasoning}")
    lines.append(f"- **Role relevance** ({c.role_relevance.score}): {c.role_relevance.reasoning}")
    lines.append(f"- **Overall fit** ({c.overall_fit.score}): {c.overall_fit.reasoning}")
    lines.append("")
    if c.gaps:
        lines.append("### Gaps")
        for gap in c.gaps:
            lines.append(f"- _{gap.category}_: {gap.detail}")
        lines.append("")
    return lines
