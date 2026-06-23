import faiss
import numpy as np
import json
import os
from typing import List, Dict, Tuple
from app.config import settings
from app.vectorstore.embeddings import embed_query, embed_texts

INDEX_PATH = os.path.join(settings.FAISS_INDEX_PATH, "index.faiss")
META_PATH = os.path.join(settings.FAISS_INDEX_PATH, "metadata.json")

_index: faiss.Index = None
_metadata: List[Dict] = []


def _load_index():
    global _index, _metadata
    if _index is not None:
        return
    if os.path.exists(INDEX_PATH) and os.path.exists(META_PATH):
        _index = faiss.read_index(INDEX_PATH)
        with open(META_PATH, "r", encoding="utf-8") as f:
            _metadata = json.load(f)


def build_index(documents: List[Dict]):
    """
    documents: [{"text": "...", "source": "...", "keywords": [...]}]
    构建 FAISS 索引并持久化
    """
    global _index, _metadata
    texts = [d["text"] for d in documents]
    embeddings = embed_texts(texts).astype(np.float32)

    dim = embeddings.shape[1]
    _index = faiss.IndexFlatIP(dim)   # 内积 = 余弦相似度（归一化后）
    _index.add(embeddings)

    os.makedirs(settings.FAISS_INDEX_PATH, exist_ok=True)
    faiss.write_index(_index, INDEX_PATH)

    _metadata = documents
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(_metadata, f, ensure_ascii=False, indent=2)


def semantic_search(query: str, top_k: int = None) -> List[Dict]:
    """纯向量检索，返回 top_k 文档"""
    _load_index()
    if _index is None or _index.ntotal == 0:
        return []

    k = top_k or settings.RAG_TOP_K
    q_vec = embed_query(query).astype(np.float32).reshape(1, -1)
    scores, indices = _index.search(q_vec, k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0 or score < settings.RAG_SCORE_THRESHOLD:
            continue
        doc = dict(_metadata[idx])
        doc["semantic_score"] = float(score)
        results.append(doc)
    return results


def keyword_search(query: str, documents: List[Dict]) -> List[Dict]:
    """简单关键词覆盖率检索"""
    query_tokens = set(query.lower().split())
    scored = []
    for doc in documents:
        keywords = set(kw.lower() for kw in doc.get("keywords", []))
        if not keywords:
            keywords = set(doc["text"].lower().split()[:20])
        overlap = query_tokens & keywords
        score = len(overlap) / max(len(keywords), 1)
        if score > 0:
            scored.append({**doc, "keyword_score": score})
    scored.sort(key=lambda x: x["keyword_score"], reverse=True)
    return scored[: settings.RAG_TOP_K]


def hybrid_search(query: str) -> Tuple[List[Dict], float]:
    """
    混合检索：向量 + 关键词融合
    返回 (docs, coverage_score)
    coverage_score 用于 Confidence Check
    """
    _load_index()
    if _index is None or _index.ntotal == 0:
        return [], 0.0

    semantic_docs = semantic_search(query)
    keyword_docs = keyword_search(query, _metadata)

    # 合并去重，语义结果优先
    seen = set()
    merged = []
    for doc in semantic_docs + keyword_docs:
        key = doc.get("source", doc["text"][:30])
        if key not in seen:
            seen.add(key)
            merged.append(doc)

    # 计算关键词覆盖率
    query_tokens = set(query.lower().split())
    all_keywords: set = set()
    for doc in merged:
        all_keywords.update(kw.lower() for kw in doc.get("keywords", []))
    coverage = len(query_tokens & all_keywords) / max(len(query_tokens), 1)

    return merged[: settings.RAG_TOP_K], coverage
