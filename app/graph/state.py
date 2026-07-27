from typing import TypedDict, Optional


class MedicalState(TypedDict):
    # ── 用户输入链路 ──
    user_id: str
    session_id: str
    original_question: str       # 用户原始输入，全程不变
    merged_question: str         # Clarify 合并后的问题，传入检索
    retrieval_query: str         # 经过改写的检索 query，与 merged_question 解耦

    # ── 状态机 ──
    session_state: str           # "active" | "clarifying" | "blocked" | ""
    clarify_question: str        # 上轮发出的追问内容
    clarify_answer: str          # 本轮用户对追问的回答

    # ── 数据源选择（Context Router 写入）──
    need_health_data: bool       # 是否需要加载 EHR 健康数据
    need_medical_knowledge: bool # 是否需要 RAG 医学知识检索

    # ── 上下文 ──
    health_context: dict         # 来自 Health Loader 的 EHR 数据
    memory_context: dict         # 来自 Memory Loader 的历史对话
    episodic_context: list       # 来自 Episodic Memory 的召回记录
    rag_context: list            # 来自 Knowledge Retriever 的召回文档

    # ── 风险控制 ──
    guardrail_result: str        # "pass" | "blocked"
    guardrail_reason: str        # blocked 时的拦截原因
    triage_level: str            # "emergency" | "urgent" | "routine"
    policy_mode: str             # "emergency" | "advisory" | "referral" | "blocked"

    # ── 置信度（双维度）──
    semantic_score: float        # 语义相似度得分 [0, 1]
    coverage_score: float        # 关键词覆盖率得分 [0, 1]
    confidence_score: float      # 加权综合置信度 [0, 1]
    need_clarify: bool           # 是否需要追问

    # ── 输出 ──
    answer: str                  # 最终生成的回答

    # ── 运行时追踪 ──
    error_log: list              # [{"node": "...", "error": "...", ...}]
