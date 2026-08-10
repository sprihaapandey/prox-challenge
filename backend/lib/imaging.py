"""Shared image helpers for anything sent to Claude vision.

A percentage grid overlay measurably improves spatial-coordinate accuracy
from vision models (verified during manual ingestion — see
ingestion/visuals.py) versus asking for raw pixel/percentage coordinates on
an unmarked image. Used both when cataloging manual pages and when
analyzing a user's uploaded photo for annotation.
"""

from __future__ import annotations

import base64
from io import BytesIO

from PIL import Image, ImageDraw

GRID_STEP_PCT = 10
GRID_COLOR = (255, 0, 0)


def with_grid_overlay(image: Image.Image) -> Image.Image:
    gridded = image.convert("RGB").copy()
    draw = ImageDraw.Draw(gridded)
    w, h = gridded.size
    for pct in range(0, 101, GRID_STEP_PCT):
        x = int(w * pct / 100)
        y = int(h * pct / 100)
        draw.line([(x, 0), (x, h)], fill=GRID_COLOR, width=1)
        draw.line([(0, y), (w, y)], fill=GRID_COLOR, width=1)
        draw.text((x + 2, 2), str(pct), fill=GRID_COLOR)
        draw.text((2, y + 2), str(pct), fill=GRID_COLOR)
    return gridded


def encode_png(image: Image.Image) -> str:
    buf = BytesIO()
    image.save(buf, format="PNG")
    return base64.standard_b64encode(buf.getvalue()).decode("utf-8")
