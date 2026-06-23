from langgraph.graph import StateGraph, END
from app.graph.state import MedicalState
from app.graph.nodes import (
    message_router_node,
    context_router_node,
    context_loader_node,
    knowledge_retriever_node,
    guardrail_node,
    triage_node,
    policy_engine_node,
    confidence_check_node,
    answer_node,
    clarify_node,
    memory_update_node,
    save_clarify_state_node,
)
from app.graph.nodes.guardrail import route_after_guardrail
from app.graph.nodes.confidence_check import route_after_confidence


def build_graph() -> StateGraph:
    graph = StateGraph(MedicalState)

    # ── 注册节点 ──────────────────────────────────────────
    graph.add_node("message_router", message_router_node)
    graph.add_node("context_router", context_router_node)
    graph.add_node("context_loader", context_loader_node)
    graph.add_node("knowledge_retriever", knowledge_retriever_node)
    graph.add_node("guardrail", guardrail_node)
    graph.add_node("triage", triage_node)
    graph.add_node("policy_engine", policy_engine_node)
    graph.add_node("confidence_check", confidence_check_node)
    graph.add_node("generate_answer", answer_node)
    graph.add_node("clarify", clarify_node)
    graph.add_node("memory_update", memory_update_node)
    graph.add_node("save_clarify_state", save_clarify_state_node)

    # ── 设置入口 ──────────────────────────────────────────
    graph.set_entry_point("message_router")

    # ── Guardrail Early Exit（前置，blocked 直接终止）──────
    graph.add_edge("message_router", "guardrail")

    graph.add_conditional_edges(
        "guardrail",
        route_after_guardrail,
        {
            "blocked": END,
            "pass": "context_router",
        },
    )

    # ── 主干线性边 ────────────────────────────────────────
    graph.add_edge("context_router", "context_loader")
    graph.add_edge("context_loader", "knowledge_retriever")
    graph.add_edge("knowledge_retriever", "triage")

    # ── 风险控制链 ────────────────────────────────────────
    graph.add_edge("triage", "policy_engine")
    graph.add_edge("policy_engine", "confidence_check")

    # ── Confidence 条件边 ─────────────────────────────────
    graph.add_conditional_edges(
        "confidence_check",
        route_after_confidence,
        {
            "answer": "generate_answer",
            "clarify": "clarify",
        },
    )

    # ── Answer 路径 ───────────────────────────────────────
    graph.add_edge("generate_answer", "memory_update")
    graph.add_edge("memory_update", END)

    # ── Clarify 路径 ──────────────────────────────────────
    graph.add_edge("clarify", "memory_update")
    graph.add_edge("memory_update", "save_clarify_state")
    graph.add_edge("save_clarify_state", END)

    return graph.compile()


# 全局编译好的 graph 实例（避免重复编译）
medical_graph = build_graph()
