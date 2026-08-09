"""Semantic search over Layer 2 (chunks, visuals, troubleshooting, weld diagnosis)."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from db.embeddings import embed_text
from db.models import Chunk, TroubleshootingEntry, Visual, WeldDiagnosis

DEFAULT_LIMIT = 5


@dataclass
class ChunkResult:
    doc_id: str
    page: int
    section: str | None
    content: str
    relevance: float


@dataclass
class VisualResult:
    id: str
    doc_id: str
    page: int
    type: str
    title: str
    description: str
    image_path: str
    highlight_bbox_pct: list
    relevance: float


def _relevance(cosine_distance: float) -> float:
    """Convert cosine distance (0=identical, 2=opposite) to a 0-1 relevance score."""
    return max(0.0, 1.0 - cosine_distance / 2.0)


def search_chunks(session: Session, query: str, doc_id: str | None = None, limit: int = DEFAULT_LIMIT) -> list[ChunkResult]:
    q_emb = embed_text(query)
    dist = Chunk.embedding.cosine_distance(q_emb)
    stmt = session.query(Chunk, dist.label("dist"))
    if doc_id:
        stmt = stmt.filter(Chunk.doc_id == doc_id)
    rows = stmt.order_by(dist).limit(limit).all()
    return [
        ChunkResult(doc_id=c.doc_id, page=c.page, section=c.section, content=c.content, relevance=_relevance(d))
        for c, d in rows
    ]


def search_visuals(session: Session, query: str, doc_id: str | None = None, limit: int = DEFAULT_LIMIT) -> list[VisualResult]:
    q_emb = embed_text(query)
    dist = Visual.embedding.cosine_distance(q_emb)
    stmt = session.query(Visual, dist.label("dist"))
    if doc_id:
        stmt = stmt.filter(Visual.doc_id == doc_id)
    rows = stmt.order_by(dist).limit(limit).all()
    return [
        VisualResult(
            id=v.id,
            doc_id=v.doc_id,
            page=v.page,
            type=v.type,
            title=v.title,
            description=v.description,
            image_path=v.image_path,
            highlight_bbox_pct=v.highlight_bbox_pct,
            relevance=_relevance(d),
        )
        for v, d in rows
    ]


def search_troubleshooting_semantic(session: Session, query: str, limit: int = DEFAULT_LIMIT) -> list[tuple[TroubleshootingEntry, float]]:
    q_emb = embed_text(query)
    dist = TroubleshootingEntry.embedding.cosine_distance(q_emb)
    rows = session.query(TroubleshootingEntry, dist.label("dist")).order_by(dist).limit(limit).all()
    return [(t, _relevance(d)) for t, d in rows]


def search_weld_diagnosis_semantic(session: Session, query: str, limit: int = DEFAULT_LIMIT) -> list[tuple[WeldDiagnosis, float]]:
    q_emb = embed_text(query)
    dist = WeldDiagnosis.embedding.cosine_distance(q_emb)
    rows = session.query(WeldDiagnosis, dist.label("dist")).order_by(dist).limit(limit).all()
    return [(w, _relevance(d)) for w, d in rows]
