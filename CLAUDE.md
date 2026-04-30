# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A teaching project that scores resume PDFs against a job description using the Claude API. Each resume goes through a pipeline: PDF parse -> structured extraction (LLM) -> scoring (LLM) -> optional self-critique (LLM). Output is a ranked JSON file and markdown report.

## Commands

```bash
# Install dependencies
uv sync

# Generate sample resume PDFs (not checked in)
uv run python scripts/generate_sample_resumes.py

# Run the pipeline
python main.py --jd sample_data/sample_jd.txt --resumes sample_data/resumes/

# Run with self-critique (adds one extra LLM call per resume)
python main.py --jd sample_data/sample_jd.txt --resumes sample_data/resumes/ --self-critique

# Run the Streamlit web UI
uv run streamlit run app.py

# Unit tests (no LLM calls, fast)
uv run pytest

# Run a single test
uv run pytest tests/test_pdf_parser.py

# Evals (makes real LLM calls, checks score ranges)
uv run python -m src.evals
```

## Environment

Requires `ANTHROPIC_API_KEY` in a `.env` file (loaded via `python-dotenv`). See `.env.example`.

## Architecture

**Core pattern repeated in every LLM module:** define a tool from a Pydantic model's JSON schema -> force Claude to call it via `tool_choice` -> validate the response back into a Pydantic object. This appears in `extractor.py`, `scorer.py`, and `critique.py`.

**Two entry points:**
- `main.py` — CLI that loops over resume PDFs sequentially
- `app.py` — Streamlit web UI with file upload

**Pipeline stages (each in its own module under `src/`):**
1. `pdf_parser.py` — pdfplumber text extraction, no LLM
2. `extractor.py` — resume text -> `CandidateProfile` (LLM call #1, tool: `record_candidate`)
3. `scorer.py` — profile + JD -> `ScoredCandidate` (LLM call #2, tool: `record_score`). Uses prompt caching on the JD text block (`cache_control: ephemeral`)
4. `critique.py` — optional review pass (LLM call #3, tool: `record_critique`)
5. `reporter.py` — writes `results.json` and `report.md`, no LLM

**Key files:**
- `src/models.py` — all Pydantic models (`CandidateProfile`, `ScoreReport`, `ScoredCandidate`, `CritiqueReport`, `ProcessingError`). These are the contracts between modules.
- `src/prompts.py` — all LLM prompts in one place. Edit prompts here, not in the module files.
- `src/evals.py` — eval harness runner
- `tests/evals/cases.py` — golden eval cases with expected score ranges (not exact values)

## Design conventions

- Default model is `claude-sonnet-4-6`, set in `src/extractor.py` as `DEFAULT_MODEL`.
- Errors in individual resumes produce a `ProcessingError` instead of crashing the batch.
- `scorer.py` also exposes `score_candidate_ensemble()` which runs N scoring calls and returns median scores per dimension.
- Evals test score ranges (e.g., 80-100 for strong match) because LLM output varies between calls. Add new eval cases by appending to `ALL_CASES` in `tests/evals/cases.py`.