from app.graph.state import MedicalState
from app.services.rag_service import hybrid_search


def knowledge_retriever_node(state: MedicalState) -> dict:
    """
    按需执行：need_medical_knowledge=True 时执行混合检索。
    返回召回文档列表和关键词覆盖率（供 Confidence Check 使用）。
    """
    if not state.get("need_medical_knowledge", False):
        return {"rag_context": [], "coverage_score": 0.0}

    query = state.get("retrieval_query") or state["merged_question"]
    docs, coverage_score = hybrid_search(query)

    return {
        "rag_context": docs,
        "coverage_score": coverage_score,
    }
