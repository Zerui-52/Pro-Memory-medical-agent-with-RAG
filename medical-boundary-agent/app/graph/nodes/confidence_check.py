from app.graph.state import MedicalState
from app.vectorstore.embeddings import embed_query
from app.config import settings
from app.database.session import get_db_session
from app.database import crud
import numpy as np


def _compute_semantic_score(question: str, rag_context: list) -> float:
    """计算问题与召回文档的最大语义相似度"""
    if not rag_context:
        return 0.0
    # 直接使用 FAISS 已返回的语义得分（已归一化）
    scores = [doc.get("semantic_score", 0.0) for doc in rag_context]
    return float(max(scores)) if scores else 0.0


def confidence_check_node(state: MedicalState) -> dict:
    """
    双维度置信度评估：
    - semantic_score：召回文档与问题的最大语义相似度
    - coverage_score：关键词覆盖率（由 Knowledge Retriever 写入）
    - confidence_score：加权综合分 = w1*semantic + w2*coverage

    confidence_score < threshold → need_clarify=True
    """
    rag_context = state.get("rag_context", [])
    coverage_score = state.get("coverage_score", 0.0)

    # 若没有做 RAG 检索，置信度直接设为较高值（纯健康档案场景）
    if not state.get("need_medical_knowledge", False):
        return {
            "semantic_score": 1.0,
            "coverage_score": 1.0,
            "confidence_score": 1.0,
            "need_clarify": False,
        }

    semantic_score = _compute_semantic_score(state["merged_question"], rag_context)

    w1 = settings.SEMANTIC_WEIGHT
    w2 = settings.COVERAGE_WEIGHT
    confidence_score = w1 * semantic_score + w2 * coverage_score

    need_clarify = confidence_score < settings.CONFIDENCE_THRESHOLD

    # 超过最大追问轮数则强制回答
    if need_clarify:
        db = get_db_session()
        try:
            cs = crud.get_clarify_state(db, state["session_id"])
            if cs and cs.clarify_round >= 3:
                need_clarify = False
        finally:
            db.close()

    return {
        "semantic_score": round(semantic_score, 4),
        "coverage_score": round(coverage_score, 4),
        "confidence_score": round(confidence_score, 4),
        "need_clarify": need_clarify,
    }


def route_after_confidence(state: MedicalState) -> str:
    """条件边路由函数：need_clarify → clarify，否则 → answer"""
    return "clarify" if state.get("need_clarify", False) else "answer"
