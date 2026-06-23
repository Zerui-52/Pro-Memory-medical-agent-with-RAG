from app.graph.state import MedicalState
from app.graph.state_machine import record_error
from app.services.llm_service import classify

TRIAGE_PROMPT = """判断以下医疗问题的紧急程度。

问题：{question}
{health_hint}

紧急程度标准：
- emergency：生命体征异常、突发胸痛/呼吸困难/意识障碍、大量出血等需要立即急救
- urgent：症状较重但非即刻危及生命，需在数小时内就医
- routine：普通健康咨询、慢病管理、预防保健等

只输出一个词：emergency 或 urgent 或 routine"""


def triage_node(state: MedicalState) -> dict:
    """
    标记问题的紧急等级 triage_level。
    结果传入 Policy Engine 决定回答策略。
    """
    question = state["merged_question"]
    health_context = state.get("health_context", {})

    # 如有健康档案，加入 prompt 提升判断准确度
    health_hint = ""
    if health_context.get("conditions"):
        health_hint = f"用户既往病史：{', '.join(health_context['conditions'])}"

    prompt = TRIAGE_PROMPT.format(question=question, health_hint=health_hint)
    error_updates = {}

    try:
        result = classify(prompt).strip().lower()
        if "emergency" in result:
            level = "emergency"
        elif "urgent" in result:
            level = "urgent"
        else:
            level = "routine"
    except Exception as e:
        level = "routine"
        error_updates = record_error(state, "triage", e)

    return {"triage_level": level, **error_updates}
