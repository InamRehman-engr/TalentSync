"""resume_parser.py — Extract text from uploaded resume files (PDF, DOCX, TXT)
and apply lightweight heuristic field extraction.
"""

from __future__ import annotations

import io
import logging
import re
from typing import Dict

logger = logging.getLogger(__name__)


# ─── Text Extraction ─────────────────────────────────────────────────────────


def _extract_pdf(file_bytes: bytes) -> str:
    """Try PyMuPDF first, fall back to pdfplumber."""
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        return text.strip()
    except ImportError:
        pass
    except Exception as exc:
        logger.warning("PyMuPDF failed: %s", exc)

    try:
        import pdfplumber

        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages).strip()
    except Exception as exc:
        logger.warning("pdfplumber failed: %s", exc)

    return ""


def _extract_docx(file_bytes: bytes) -> str:
    try:
        from docx import Document

        doc = Document(io.BytesIO(file_bytes))
        return "\n".join(para.text for para in doc.paragraphs).strip()
    except Exception as exc:
        logger.warning("DOCX extraction failed: %s", exc)
        return ""


def extract_text(filename: str, file_bytes: bytes) -> str:
    """Return plain text from a resume file. Returns '' on failure."""
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else "txt"
    if ext == "pdf":
        return _extract_pdf(file_bytes)
    if ext in ("docx", "doc"):
        return _extract_docx(file_bytes)
    # TXT / fallback
    try:
        return file_bytes.decode("utf-8", errors="replace").strip()
    except Exception:
        return ""


# ─── Heuristic Field Extraction ──────────────────────────────────────────────

_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
_PHONE_RE = re.compile(r"[\+]?[\d][\d\s\-\(\)\.]{7,14}[\d]")
_EXP_RE = re.compile(r"(\d+)\+?\s*(?:years?|yrs?)[\s\S]{0,20}?(?:experience|exp)", re.IGNORECASE)

_SECTION_HEADERS = re.compile(
    r"^(skills?|technical\s+skills?|core\s+competencies|technologies|"
    r"experience|work\s+(?:experience|history)|employment|"
    r"education|academic|certifications?|"
    r"summary|objective|profile|about\s*me|professional\s+summary|"
    r"projects?|achievements?|awards?)",
    re.IGNORECASE,
)

_SKILLS_HEADER = re.compile(
    r"^(skills?|technical\s+skills?|core\s+competencies|technologies)", re.IGNORECASE
)
_SUMMARY_HEADER = re.compile(
    r"^(summary|objective|profile|about\s*me|professional\s+summary)", re.IGNORECASE
)
_EDUCATION_HEADER = re.compile(r"^(education|academic\s+background|academic)", re.IGNORECASE)
_TITLE_KEYWORDS = {
    "engineer", "developer", "analyst", "manager", "designer", "scientist",
    "architect", "consultant", "specialist", "director", "lead", "officer",
    "administrator", "coordinator", "executive", "intern",
}


def heuristic_parse(text: str) -> Dict:
    """Extract structured fields from raw resume text."""
    result: Dict = {
        "name": "",
        "email": "",
        "phone": "",
        "title": "",
        "experience": 0,
        "skills": "",
        "education": "",
        "summary": "",
    }

    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]

    # ── Email ──────────────────────────────────────────────────────────────
    for line in lines:
        m = _EMAIL_RE.search(line)
        if m:
            result["email"] = m.group(0).lower()
            break

    # ── Phone ──────────────────────────────────────────────────────────────
    for line in lines[:20]:
        m = _PHONE_RE.search(line)
        if m:
            digits = re.sub(r"\D", "", m.group(0))
            if 7 <= len(digits) <= 15:
                result["phone"] = m.group(0).strip()
                break

    # ── Name — first short line that looks like a person's name ───────────
    for line in lines[:6]:
        if _EMAIL_RE.search(line) or re.search(r"http|www\.|linkedin\.com|github\.com", line, re.IGNORECASE):
            continue
        words = line.split()
        if 2 <= len(words) <= 5 and not _SECTION_HEADERS.match(line):
            # Rough name heuristic: most words start with uppercase
            upper_ratio = sum(1 for w in words if w and w[0].isupper()) / len(words)
            if upper_ratio >= 0.6:
                result["name"] = line
                break

    # ── Experience years ───────────────────────────────────────────────────
    m = _EXP_RE.search(text)
    if m:
        result["experience"] = min(int(m.group(1)), 50)

    # ── Job Title — first line in the top 10 that contains a title keyword ─
    for line in lines[:10]:
        if any(kw in line.lower() for kw in _TITLE_KEYWORDS) and len(line.split()) <= 8:
            result["title"] = line
            break

    # ── Section extraction ─────────────────────────────────────────────────
    sections: Dict[str, list] = {}
    current_section: str | None = None
    for line in lines:
        h = _SECTION_HEADERS.match(line)
        if h:
            current_section = h.group(1).lower().split()[0]  # first word as key
            sections.setdefault(current_section, [])
        elif current_section is not None:
            sections[current_section].append(line)

    # Skills
    for key in ("skills", "technical", "core", "technologies"):
        if key in sections:
            result["skills"] = " | ".join(sections[key])[:500]
            break

    # Summary
    for key in ("summary", "objective", "profile", "about"):
        if key in sections:
            result["summary"] = " ".join(sections[key])[:500]
            break

    # Education
    for key in ("education", "academic"):
        if key in sections:
            result["education"] = " ".join(sections[key][:3])[:300]
            break

    return result
