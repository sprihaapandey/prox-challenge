"""Render every page of a manual PDF to a PNG image, preserving page numbers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pypdfium2 as pdfium

RENDER_SCALE = 2.0  # ~144 DPI, good balance of legibility vs. file size


@dataclass
class RenderedPage:
    page_number: int  # 1-indexed
    image_path: Path
    width_px: int
    height_px: int


def render_document(pdf_path: Path, out_dir: Path, scale: float = RENDER_SCALE) -> list[RenderedPage]:
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf = pdfium.PdfDocument(str(pdf_path))
    pages: list[RenderedPage] = []
    for i in range(len(pdf)):
        page = pdf[i]
        bitmap = page.render(scale=scale)
        pil_image = bitmap.to_pil()
        page_number = i + 1
        image_path = out_dir / f"page_{page_number:03d}.png"
        pil_image.save(image_path)
        pages.append(
            RenderedPage(
                page_number=page_number,
                image_path=image_path,
                width_px=pil_image.width,
                height_px=pil_image.height,
            )
        )
    return pages
