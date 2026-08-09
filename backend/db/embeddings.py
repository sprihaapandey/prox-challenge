"""Local embedding model — no external API key needed for semantic search.

Anthropic doesn't offer a first-party embeddings endpoint, and the challenge
requires the whole app to run on a single ANTHROPIC_API_KEY. sentence-transformers
runs entirely locally, so semantic search doesn't add a second API dependency.
"""

from __future__ import annotations

from functools import lru_cache

from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_model()
    vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return [v.tolist() for v in vectors]


def embed_text(text: str) -> list[float]:
    return embed_texts([text])[0]
