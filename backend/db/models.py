"""SQLAlchemy models for the three knowledge layers.

Layer 1 (raw source) lives on disk as files/*.pdf and data/pages/*.png —
referenced by path from the models below, not duplicated in the database.

Layer 2 (semantic knowledge): Chunk and Visual, both embedded for
similarity search.

Layer 3 (structured facts): DutyCycle, Polarity, TroubleshootingEntry,
WeldDiagnosis, Part — deterministic records tools look up exactly rather
than asking the LLM to re-derive them.
"""

from __future__ import annotations

from pgvector.sqlalchemy import Vector
from sqlalchemy import Integer, JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

EMBEDDING_DIM = 384  # sentence-transformers/all-MiniLM-L6-v2


class Base(DeclarativeBase):
    pass


# --- Layer 2: semantic knowledge -------------------------------------------------


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    doc_id: Mapped[str] = mapped_column(String, index=True)
    page: Mapped[int] = mapped_column(Integer, index=True)
    section: Mapped[str | None] = mapped_column(String, nullable=True)
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM))


class Visual(Base):
    __tablename__ = "visuals"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    doc_id: Mapped[str] = mapped_column(String, index=True)
    page: Mapped[int] = mapped_column(Integer, index=True)
    type: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)
    image_path: Mapped[str] = mapped_column(String)
    highlight_bbox_pct: Mapped[list] = mapped_column(JSON)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM))


# --- Layer 3: structured facts -------------------------------------------------


class DutyCycle(Base):
    __tablename__ = "duty_cycle"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    process: Mapped[str] = mapped_column(String, index=True)
    input_voltage: Mapped[int] = mapped_column(Integer, index=True)
    amperage: Mapped[int] = mapped_column(Integer, index=True)
    duty_cycle_percent: Mapped[int] = mapped_column(Integer)
    welding_current_range: Mapped[str] = mapped_column(String)
    source_page: Mapped[int] = mapped_column(Integer)


class Polarity(Base):
    __tablename__ = "polarity"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    process: Mapped[str] = mapped_column(String, index=True)
    polarity_name: Mapped[str] = mapped_column(String)
    polarity_full_name: Mapped[str] = mapped_column(String)
    gun_or_torch_or_electrode_cable: Mapped[str] = mapped_column(String)
    gun_or_torch_or_electrode_socket: Mapped[str] = mapped_column(String)
    ground_clamp_socket: Mapped[str] = mapped_column(String)
    applies_to: Mapped[str] = mapped_column(Text)
    source_page: Mapped[int] = mapped_column(Integer)


class TroubleshootingEntry(Base):
    __tablename__ = "troubleshooting"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    process: Mapped[str] = mapped_column(String, index=True)
    symptom: Mapped[str] = mapped_column(String, index=True)
    possible_causes: Mapped[list] = mapped_column(JSON)
    recommended_actions: Mapped[list] = mapped_column(JSON)
    source_pages: Mapped[list] = mapped_column(JSON)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM))


class WeldDiagnosis(Base):
    __tablename__ = "weld_diagnosis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    process: Mapped[str] = mapped_column(String, index=True)
    defect_name: Mapped[str] = mapped_column(String, index=True)
    visual_description: Mapped[str] = mapped_column(Text)
    possible_causes_and_solutions: Mapped[list] = mapped_column(JSON)
    source_page: Mapped[int] = mapped_column(Integer)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM))


class Part(Base):
    __tablename__ = "parts"

    part_number: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(String, index=True)
    qty: Mapped[int] = mapped_column(Integer)
    source_page: Mapped[int] = mapped_column(Integer)
    diagram_page: Mapped[int] = mapped_column(Integer)
