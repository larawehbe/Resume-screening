# Building the Resume Matcher Step by Step

This guide walks you through building the project from scratch. Each step produces something you can run and test before moving on.

## Step 1: Define the data models (`src/models.py`)

Start here because everything else depends on these shapes. You'll see what data flows through the pipeline before writing any logic.

- `CandidateProfile` — what we extract from a resume (name, skills, past roles, etc.)
- `DimensionScore` — a score from 0-100 with a reasoning string
- `Gap` — a specific missing skill or experience shortfall
- `ScoreReport` — what the scorer LLM returns (four dimension scores + reasoning + gaps)
- `ScoredCandidate` — a candidate profile combined with its scores
- `ProcessingError` — what we record when a resume fails at any stage
- `CritiqueReport` — for the optional self-critique step

## Step 2: Parse a PDF (`src/pdf_parser.py`)

First piece of real logic, and no API key needed. You can run it immediately.

- Use `pdfplumber` to open a PDF and extract text from every page
- Clean up the whitespace
- Test it: pass a PDF file path, print the text you get back

## Step 3: Write the prompts (`src/prompts.py`)

Before making any LLM calls, write what you'll say to Claude. You can read and discuss the prompts without spending any API credits.

- `EXTRACTION_SYSTEM_PROMPT` — tells Claude to act as a resume parser
- `SCORING_SYSTEM_PROMPT` — tells Claude to act as a hiring evaluator
- `CRITIQUE_SYSTEM_PROMPT` — tells Claude to act as a senior hiring manager reviewing scores

## Step 4: Extract a candidate profile (`src/extractor.py`)

First LLM call. This is where you learn the core pattern that repeats throughout the project:

1. Define a tool from a Pydantic schema (`CandidateProfile.model_json_schema()`)
2. Send a message to Claude and force it to call that tool with `tool_choice`
3. Find the `tool_use` block in the response
4. Validate the response with `CandidateProfile.model_validate()`

This guarantees Claude returns structured JSON matching your schema, not free-form text.

Test it: parse one PDF from step 2, pass the text to `extract_candidate()`, print the profile.

## Step 5: Score a candidate (`src/scorer.py`)

Second LLM call. Same pattern as step 4, but with a different prompt and schema.

- Define a tool from `ScoreReport.model_json_schema()`
- Send the job description + candidate profile to Claude
- Claude scores 4 dimensions (0-100): skills_match, experience_match, role_relevance, overall_fit
- Validate the response into a `ScoreReport`, then wrap it into a `ScoredCandidate`

Students see the pattern repeat and it clicks.

Test it: take the profile from step 4, score it against the sample JD, print the scores.

## Step 6: Write the output (`src/reporter.py`)

No LLM calls here. Take the list of results and write two files:

- `results.json` — machine-readable ranked list of candidates plus any errors
- `report.md` — human-readable markdown report with a table and per-candidate details

## Step 7: Wire it all together (`main.py`)

Now connect everything into a working CLI:

- Load the API key from `.env` using `load_dotenv()`
- Read the job description from a text file
- List the resumes directory and find all `.pdf` files
- Loop through each PDF: parse -> extract -> score
- If any step fails for a resume, record a `ProcessingError` and keep going
- Write `results.json` and `report.md` to the output directory

This is where `process_one()` and `run()` come in.

Run it:
```bash
python main.py --jd sample_data/sample_jd.txt --resumes sample_data/resumes/
```

## Step 8 (optional): Add self-critique (`src/critique.py`)

Third LLM call. Same tool use pattern again.

- Send the JD + profile + original scores to Claude as a "senior hiring manager"
- Claude decides if any score is off by more than 10 points
- If yes, it returns corrected scores. If no, it keeps the originals.

By this point you've seen the tool use + Pydantic pattern three times and can write it yourself.

Run it with the flag:
```bash
python main.py --jd sample_data/sample_jd.txt --resumes sample_data/resumes/ --self-critique
```

## Build order summary

```
1. models.py       — define the data shapes
2. pdf_parser.py   — parse PDFs (no LLM)
3. prompts.py      — write the prompts (no LLM)
4. extractor.py    — first LLM call (learn the tool use pattern)
5. scorer.py       — second LLM call (same pattern repeats)
6. reporter.py     — write output files (no LLM)
7. main.py         — wire everything together
8. critique.py     — optional third LLM call (pattern repeats again)
```

The key idea: you learn the **tool use + Pydantic** pattern once in step 4, then see it repeat in steps 5 and 8. By the third time, you can write it yourself.
