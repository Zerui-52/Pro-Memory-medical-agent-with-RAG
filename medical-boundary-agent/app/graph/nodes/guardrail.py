from app.graph.state import MedicalState
from app.graph.state_machine import record_error
from app.services.llm_service import classify

GUARDRAIL_PROMPT = """你是医疗对话安全审核员。判断以下问题是否安全可以回答。

问题：{question}

以下情况必须拦截（输出 blocked）：
- 询问非法药物获取方式
- 要求提供处方药剂量以达到危险目的
- 明显自我伤害意图
- 与医疗完全无关的内容

其他医疗咨询问题均可通过（输出 pass）。

只输出一个词：pass 或 blocked"""

GUARDRAIL_REASON_PROMPT = """用一句话说明为什么以下医疗问题被拦截：

问题：{question}

只输出原因，不超过30字。"""


def guardrail_node(state: MedicalState) -> dict:
    """
    安全检测节点。
    guardrail_result = "pass" 继续流程。
    guardrail_result = "blocked" 触发条件边直接到 END。
    """
    question = state["merged_question"]
    error_updates = {}

    try:
        result = classify(GUARDRAIL_PROMPT.format(question=question)).strip().lower()
        is_blocked = "blocked" in result
    except Exception as e:
        is_blocked = False
        error_updates = record_error(state, "guardrail", e)

    if is_blocked:
        try:
            from app.services.llm_service import chat
            reason = chat(
                system="你是安全审核助手",
                user=GUARDRAIL_REASON_PROMPT.format(question=question),
                temperature=0,
            ).strip()
        except Exception:
            reason = "该问题不符合医疗咨询安全规范"

        return {
            "guardrail_result": "blocked",
            "guardrail_reason": reason,
            "session_state": "blocked",
            "answer": f"抱歉，无法回答该问题。原因：{reason}",
        }

    return {
        "guardrail_result": "pass",
        "guardrail_reason": "",
        "session_state": "active",
        **error_updates,
    }


def route_after_guardrail(state: MedicalState) -> str:
    """条件边路由函数：blocked → END，pass → triage"""
    return "blocked" if state.get("guardrail_result") == "blocked" else "pass"
