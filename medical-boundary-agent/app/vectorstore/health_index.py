import faiss
import numpy as np
import json
import os
import threading
from typing import List, Dict, Optional
from app.config import settings
from app.vectorstore.embeddings import embed_texts, embed_query

INDEX_DIR = settings.FAISS_INDEX_PATH
INDEX_PATH = os.path.join(INDEX_DIR, "health_index.faiss")
META_PATH = os.path.join(INDEX_DIR, "health_meta.json")

_lock = threading.Lock()
_index: Optional[faiss.Index] = None
_metadata: List[Dict] = []


def _ensure_dir():
    os.makedirs(INDEX_DIR, exist_ok=True)


def _load():
    global _index, _metadata
    if _index is not None:
        return
    _ensure_dir()
    if os.path.exists(INDEX_PATH) and os.path.exists(META_PATH):
        _index = faiss.read_index(INDEX_PATH)
        with open(META_PATH, "r", encoding="utf-8") as f:
            _metadata = json.load(f)


def _save():
    global _index, _metadata
    _ensure_dir()
    faiss.write_index(_index, INDEX_PATH)
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(_metadata, f, ensure_ascii=False, indent=2)


def index_health(user_id: str, items: List[Dict]):
    """
    items: [{"category": "condition|medication|allergy", "value": "..."}]
    索引用户健康数据，同一用户的旧数据会被替换。
    """
    global _index, _metadata
    with _lock:
        _load()

        # 去掉该用户的旧条目
        keep = [m for m in _metadata if m.get("user_id") != user_id]
        if keep:
            texts_keep = [m["text"] for m in keep]
            vecs_keep = embed_texts(texts_keep).astype(np.float32)
            dim = vecs_keep.shape[1]
            _index = faiss.IndexFlatIP(dim)
            _index.add(vecs_keep)
            _metadata = keep
        else:
            _index = None
            _metadata = []

        # 添加新条目
        new_texts = [item["value"] for item in items]
        if not new_texts:
            _save()
            return
        vecs = embed_texts(new_texts).astype(np.float32)
        if _index is None:
            dim = vecs.shape[1]
            _index = faiss.IndexFlatIP(dim)
        _index.add(vecs)
        for item in items:
            _metadata.append({
                "user_id": user_id,
                "category": item["category"],
                "text": item["value"],
            })
        _save()


def search_health(query: str, user_id: str, top_k: int = 3) -> List[Dict]:
    global _index, _metadata
    with _lock:
        _load()
        if _index is None or _index.ntotal == 0:
            return []

        q_vec = embed_query(query).astype(np.float32).reshape(1, -1)
        k = min(top_k * 3, _index.ntotal)
        scores, indices = _index.search(q_vec, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(_metadata) or score < 0.5:
                continue
            meta = dict(_metadata[idx])
            if meta.get("user_id") != user_id:
                continue
            meta["score"] = float(score)
            results.append(meta)
        return results[:top_k]
