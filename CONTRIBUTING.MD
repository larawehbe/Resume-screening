# Contribution Challenges — Resume Matcher

This codebase is the seed. Here's how we grow it together. Pick a challenge that matches your level, build it, open a pull request.

## Rules of engagement

- One challenge per PR — keep scope tight.
- Update `CLAUDE.md` if you introduce new conventions.
- Include the prompt(s) you used in the PR description, or save them under `prompts/`. The prompt is the teaching artifact.
- Update the `README.md` if your change affects how the project runs.
- Verify your work the way the project already does — pytest for deterministic code, evals for LLM behavior, or a scripted walkthrough. Match the existing pattern, don't invent a new one.

---

## Tier 1 — Quick wins (a few hours)

### 1. Add a 5th eval case
Pick a scenario the current cases miss — for example, a "career changer" with strong skills in one domain applying to a JD in another. Write the resume, the JD, and the expected score ranges. Submit the case in `tests/evals/cases.py` along with a short write-up of why this case catches something the existing three didn't.

### 2. CSV export of results
Add a new flag `--csv` that writes a flat CSV alongside the JSON and markdown output. Pure logic, no LLM. Tests required.

### 3. Score histogram in the markdown report
Add a small ASCII bar chart at the top of `report.md` showing the distribution of `overall_fit` scores across candidates. Visual feedback for the recruiter at a glance.

### 4. Configurable scoring dimensions
Right now there are four hardcoded dimensions (skills, experience, role relevance, overall fit). Make them configurable via a YAML or TOML file. The prompt and the Pydantic schema should both update from one source of truth.

---

## Tier 2 — Real design work (a weekend)

### 5. Add a "deep-dive" pipeline stage
After scoring, take the top N candidates and run one more LLM call that writes a paragraph for a hiring manager — pros, cons, suggested interview questions. New module, new prompt, follows the existing tool-use pattern.

### 6. Parallel processing
Process N resumes concurrently with a configurable concurrency limit. Prompt caching on the JD becomes an architectural decision, not an afterthought. Submit benchmarks: time and cost, before vs after.

### 7. Eval set generator
Write a script that takes a JD and uses Claude to generate N synthetic resumes at varying match levels, then appends them to `tests/evals/cases.py` as new cases. Self-improving evals.

### 8. Cost reporter
After every run, print and save a breakdown: total input tokens, output tokens, cache hits, cost in USD. Use the `usage` field on each API response. Most engineers have never actually looked at it.

---

## Tier 3 — Flagship (a week or more)

### 9. Web UI
Build a Streamlit or React frontend. Upload a JD and a folder of resumes, watch the pipeline run with a progress bar, see ranked results inline. Match the polish of the Tasklet React dashboard. Portfolio-grade.

### 10. Multilingual support
Resumes in any language, JD in English — or vice versa. Requires prompt engineering on both extraction and scoring, plus a multilingual eval case.

### 11. Bias audit mode
Run the same resume multiple times with name, gender, or age signals swapped. Compare the scores. Report any systematic differences. Genuinely important for a real hiring tool, and a strong teaching artifact in its own right.