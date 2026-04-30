"""Tests for pdf_parser.py."""

from pathlib import Path

import pytest

from src.pdf_parser import parse_pdf


def test_parse_pdf_raises_on_missing_file(tmp_path: Path) -> None:
    missing = tmp_path / "does_not_exist.pdf"
    with pytest.raises(Exception):
        parse_pdf(missing)


def test_parse_pdf_raises_on_non_pdf(tmp_path: Path) -> None:
    not_a_pdf = tmp_path / "note.pdf"
    not_a_pdf.write_text("This is not a PDF file.")
    with pytest.raises(Exception):
        parse_pdf(not_a_pdf)


FIXTURES = Path(__file__).parent / "fixtures"


@pytest.mark.skipif(
    not (FIXTURES / "sample_resume.pdf").exists(),
    reason="Fixture PDF not checked in; run scripts/generate_sample_resumes.py first.",
)
def test_parse_pdf_extracts_known_text() -> None:
    text = parse_pdf(FIXTURES / "sample_resume.pdf")
    assert text.strip(), "parsed text should be non-empty"
