"""Extract plain text from resume files (PDF, TXT, DOCX) and ZIP archives."""

from __future__ import annotations

import io
import logging
import re
import zipfile
import xml.etree.ElementTree as ET
from typing import Iterator

import fitz  # pymupdf

log = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".docx", ".md", ".rtf"}
DOCX_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
DOCX_TAG = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"


def _name_from_filename(filename: str) -> str:
    base = filename.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    name = re.sub(r"\.[^.]+$", "", base)
    name = re.sub(r"[_\-]+", " ", name).strip()
    return name.title() if name else "Unknown Candidate"


def _extract_pdf(data: bytes) -> str:
    doc = fitz.open(stream=data, filetype="pdf")
    try:
        parts = [page.get_text() for page in doc]
        return "\n".join(parts).strip()
    finally:
        doc.close()


def _extract_docx(data: bytes) -> str:
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        xml_content = zf.read("word/document.xml")
    root = ET.fromstring(xml_content)
    texts = [node.text for node in root.iter(DOCX_TAG) if node.text]
    return " ".join(texts).strip()


def _extract_plain(data: bytes) -> str:
    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            return data.decode(encoding).strip()
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="ignore").strip()


def extract_text_from_file(filename: str, data: bytes) -> str:
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext == ".pdf":
        return _extract_pdf(data)
    if ext == ".docx":
        return _extract_docx(data)
    if ext in {".txt", ".md", ".rtf"}:
        return _extract_plain(data)
    raise ValueError(f"Unsupported file type: {ext or filename}")


def iter_resume_files(
    filename: str,
    data: bytes,
) -> Iterator[tuple[str, bytes]]:
    """Yield (inner_filename, file_bytes) from a single file or ZIP archive."""
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext == ".zip":
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                inner_name = info.filename.rsplit("/", 1)[-1]
                if inner_name.startswith(".") or inner_name.startswith("__MACOSX"):
                    continue
                inner_ext = "." + inner_name.rsplit(".", 1)[-1].lower() if "." in inner_name else ""
                if inner_ext not in SUPPORTED_EXTENSIONS:
                    continue
                try:
                    yield inner_name, zf.read(info)
                except Exception:
                    log.exception("Failed to read %s from zip %s", inner_name, filename)
        return
    if ext in SUPPORTED_EXTENSIONS:
        yield filename, data
        return
    raise ValueError(f"Unsupported file type: {ext or filename}. Use PDF, TXT, DOCX, or ZIP.")


def parse_resume_upload(filename: str, data: bytes) -> tuple[list[dict], list[str]]:
    """Parse one uploaded file (or zip) into resume dicts ready for DB insert."""
    results: list[dict] = []
    errors: list[str] = []

    try:
        for inner_name, file_data in iter_resume_files(filename, data):
            try:
                text = extract_text_from_file(inner_name, file_data)
                if not text or len(text) < 30:
                    errors.append(f"{inner_name}: too little text extracted")
                    continue
                results.append({
                    "candidate_name": _name_from_filename(inner_name),
                    "resume_text": text,
                    "source_filename": inner_name,
                })
            except Exception as exc:
                log.exception("Failed to parse %s", inner_name)
                errors.append(f"{inner_name}: {exc}")
    except ValueError as exc:
        raise exc
    except Exception as exc:
        raise ValueError(str(exc)) from exc

    if not results:
        detail = "; ".join(errors) if errors else "No supported resume files found."
        raise ValueError(detail)

    return results, errors
