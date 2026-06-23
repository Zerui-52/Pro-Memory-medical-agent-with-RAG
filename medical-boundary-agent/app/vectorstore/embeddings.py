from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from app.config import settings

_model: SentenceTransformer = None


def get_embedding_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _model


def embed_texts(texts: List[str]) -> np.ndarray:
    model = get_embedding_model()
    return model.encode(texts, normalize_embeddings=True)


def embed_query(query: str) -> np.ndarray:
    return embed_texts([query])[0]
