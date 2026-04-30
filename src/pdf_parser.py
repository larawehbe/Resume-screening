"""
PDF -> plain text. No LLM calls here, just text extraction.

We use pdfplumber because resumes often have columns, tables, and custom
layouts that simpler libraries (like pypdf) mangle. pdfplumber handles
those well enough that the downstream LLM can make sense of the text.
"""

import re

import pdfplumber


def parse_pdf(path: str) -> str:
    """Read a resume PDF and return its text content.

    Raises an exception if the PDF can't be read or contains no text —
    the caller catches it and reports the resume as failed.
    """
    with pdfplumber.open(path) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]

    text = "\n\n".join(p for p in pages if p.strip())
    text = _normalise_whitespace(text)

    if not text.strip():
        raise ValueError("PDF parsed successfully but contained no text.")

    return text


def _normalise_whitespace(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
