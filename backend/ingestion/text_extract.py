"""Text extraction with page/section metadata, preserving manual structure.

Two extraction quirks in this manual are handled explicitly:

1. Every page carries a vertical sidebar of section tabs (Safety, Controls,
   Wire, TIG/Stick, Welding Tips, Maintenance) rendered as rotated text.
   Naive extraction interleaves these as garbled fragments. We filter by
   `char["upright"]` to drop rotated glyphs before extracting text.
2. Most content pages use a two-column layout. A single full-width text
   extraction interleaves the two columns mid-sentence. We split each page
   into left/right halves and extract each independently.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import pdfplumber

HEADER_RE = re.compile(
    r"^(Page\s+\d+|Item\s+\d+)\s+.*?(Item\s+\d+|Page\s+\d+)\s*$",
    re.IGNORECASE,
)
TOC_ENTRY_RE = re.compile(r"^(.*?[A-Za-z)])\s*\.{2,}\s*(\d+)\s*$")


@dataclass
class Section:
    title: str
    start_page: int
    end_page: int


@dataclass
class PageText:
    page_number: int
    section: str | None
    text: str


@dataclass
class DocumentText:
    doc_id: str
    sections: list[Section] = field(default_factory=list)
    pages: list[PageText] = field(default_factory=list)


def _clean_page_text(raw: str) -> str:
    lines = raw.split("\n")
    if lines and HEADER_RE.match(lines[0].strip()):
        lines = lines[1:]
    # Drop stray blank lines left by the removed header.
    while lines and not lines[0].strip():
        lines = lines[1:]
    return "\n".join(lines).strip()


def _extract_page_text(page: pdfplumber.page.Page) -> str:
    upright = page.filter(lambda obj: obj.get("object_type") != "char" or obj.get("upright", True))
    width, height = page.width, page.height
    left = upright.crop((0, 0, width / 2, height)).extract_text() or ""
    right = upright.crop((width / 2, 0, width, height)).extract_text() or ""
    combined = "\n".join(part for part in (left, right) if part.strip())
    return _clean_page_text(combined)


def _extract_toc(pdf: pdfplumber.PDF, search_pages: int = 5) -> list[Section]:
    entries: list[tuple[str, int]] = []
    for page in pdf.pages[:search_pages]:
        text = _extract_page_text(page)
        for line in text.split("\n"):
            m = TOC_ENTRY_RE.match(line.strip())
            if m:
                title = m.group(1).strip().rstrip(".")
                page_num = int(m.group(2))
                entries.append((title, page_num))
    if len(entries) < 2:
        return []
    entries.sort(key=lambda e: e[1])
    sections: list[Section] = []
    for i, (title, start) in enumerate(entries):
        end = entries[i + 1][1] - 1 if i + 1 < len(entries) else start
        sections.append(Section(title=title, start_page=start, end_page=max(end, start)))
    # Extend the last section to cover the rest of the document.
    if sections:
        sections[-1] = Section(sections[-1].title, sections[-1].start_page, 10_000)
    return sections


def _section_for_page(sections: list[Section], page_number: int) -> str | None:
    for section in sections:
        if section.start_page <= page_number <= section.end_page:
            return section.title
    return None


def extract_document_text(pdf_path: Path, doc_id: str) -> DocumentText:
    with pdfplumber.open(str(pdf_path)) as pdf:
        sections = _extract_toc(pdf)
        pages: list[PageText] = []
        for i, page in enumerate(pdf.pages):
            page_number = i + 1
            text = _extract_page_text(page)
            section = _section_for_page(sections, page_number)
            pages.append(PageText(page_number=page_number, section=section, text=text))
    # Clamp the synthetic "extend to end" sentinel to the real last page.
    if sections:
        last_page = pages[-1].page_number if pages else sections[-1].start_page
        sections[-1] = Section(sections[-1].title, sections[-1].start_page, last_page)
    return DocumentText(doc_id=doc_id, sections=sections, pages=pages)
