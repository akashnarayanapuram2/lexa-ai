"""
Phase 1 & 2: Text Extraction and Clause Splitting
Supports PDF (via PyMuPDF) and DOCX (via python-docx)
"""

import re
import fitz  # PyMuPDF
from docx import Document
import io


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract and clean text from PDF bytes."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages = []
    for page in doc:
        text = page.get_text("text")
        pages.append(text)
    doc.close()
    raw = "\n".join(pages)
    return _clean_text(raw)


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract and clean text from DOCX bytes."""
    doc = Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    raw = "\n".join(paragraphs)
    return _clean_text(raw)


def _clean_text(text: str) -> str:
    """Remove noise, fix spacing, normalize whitespace."""
    # Remove excessive whitespace / newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    # Remove page numbers (standalone digits on a line)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
    # Remove common header/footer noise
    text = re.sub(r'CONFIDENTIAL|Page \d+ of \d+', '', text, flags=re.IGNORECASE)
    return text.strip()


def split_into_clauses(text: str) -> list[dict]:
    """
    Split contract text into individual clauses.
    Detects numbered sections, lettered subsections, and bold headings.
    Returns list of {index, heading, text} dicts.
    """
    # Patterns for clause detection
    patterns = [
        # "1.", "1.1", "1.1.1" style
        r'(?m)^(\d+(?:\.\d+)*\.?\s+[A-Z][^\n]{3,80})',
        # "ARTICLE I", "SECTION 1" style
        r'(?m)^((?:ARTICLE|SECTION|CLAUSE)\s+[IVXLCDM\d]+[.:]\s*[^\n]{0,80})',
        # ALL CAPS headings (min 3 words)
        r'(?m)^([A-Z][A-Z\s]{10,60}(?:\.|:))',
    ]

    # Try to find clause boundaries
    combined = '|'.join(f'({p})' for p in patterns)
    matches = list(re.finditer(combined, text))

    clauses = []
    if not matches:
        # Fallback: split by double newlines into paragraphs
        chunks = [c.strip() for c in text.split('\n\n') if len(c.strip()) > 80]
        for i, chunk in enumerate(chunks):
            first_line = chunk.split('\n')[0][:80]
            clauses.append({
                "index": i + 1,
                "heading": first_line,
                "text": chunk,
            })
        return clauses

    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        clause_text = text[start:end].strip()
        if len(clause_text) < 40:
            continue
        heading = match.group().split('\n')[0].strip()[:120]
        clauses.append({
            "index": i + 1,
            "heading": heading,
            "text": clause_text,
        })

    # If we got too few real clauses, fall back to paragraphs
    if len(clauses) < 3:
        return split_into_clauses.__wrapped__(text) if hasattr(split_into_clauses, '__wrapped__') else _paragraph_fallback(text)

    return clauses


def _paragraph_fallback(text: str) -> list[dict]:
    chunks = [c.strip() for c in text.split('\n\n') if len(c.strip()) > 80]
    return [{"index": i + 1, "heading": c.split('\n')[0][:80], "text": c}
            for i, c in enumerate(chunks)]
