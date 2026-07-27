from typing import List, Dict
from app.vectorstore.embeddings import embed_query
import numpy as np


def vector_search(query: str, cluster: str = "default", top_k: int = 5) -> List[Dict]:
    q_vec = embed_query(query)
    return [{"text": "", "source": "episodic", "semantic_score": 0.0}]
