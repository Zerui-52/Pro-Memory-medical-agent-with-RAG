from app.graph.state import MedicalState
from app.services.llm_service import chat
from app.services.health_service import format_health_context_for_prompt
from app.services.memory_service import format_memory_for_prompt
from app.services.policy_service import get_policy_rules

ANSWER_SYSTEM = """你是一个专业的医疗健康助手。根据提供的上下文信息，给出准确、清晰的医疗健康回答。
回答要：
1. 结合用户的具体健康状况（如有）
2. 基于检索到的医学知识
3. 语言通俗易懂，避免过度专业术语
4. 严格遵守回答策略要求"""

ANSWER_PROMPT = """## 用户健康档案
{health_context}

## 历史对话
{memory_context}

## 参考医学知识
{rag_context}

## 回答策略
当前模式：{policy_mode}
{policy_instruction}

## 用户问题
{question}

请基于以上信息回答用户问题。"""

POLICY_INSTRUCTIONS = {
    "emergency": "必须在回答开头提醒用户立即寻求紧急医疗救治，然后再给出简要建议。",
    "advisory": "给出详细的健康建议，最后附上免责声明。",
    "referral": "建议用户就医，并说明为什么需要专业医生评估。",
    "blocked": "礼貌拒绝并说明原因。",
}


def answer_node(state: MedicalState) -> dict:
    """
    生成最终回答。
    读取 policy_mode 决定回答策略，读取所有上下文生成内容。
    """
    policy_mode = state.get("policy_mode", "advisory")
    rules = get_policy_rules(policy_mode)

    # 格式化各上下文
    health_str = format_health_context_for_prompt(state.get("health_context", {}))
    memory_str = format_memory_for_prompt(state.get("memory_context", {}))

    rag_docs = state.get("rag_context", [])
    rag_str = "\n\n".join(
        f"[{i+1}] {doc['text']}" for i, doc in enumerate(rag_docs[:3])
    ) if rag_docs else "（无相关医学知识）"

    prompt = ANSWER_PROMPT.format(
        health_context=health_str,
        memory_context=memory_str,
        rag_context=rag_str,
        policy_mode=policy_mode,
        policy_instruction=POLICY_INSTRUCTIONS.get(policy_mode, ""),
        question=state["merged_question"],
    )

    raw_answer = chat(
        system=ANSWER_SYSTEM,
        user=prompt,
        temperature=rules["temperature"],
        max_tokens=rules["max_tokens"],
    )

    # 附加 policy 前后缀
    final_answer = rules["prefix"] + raw_answer + rules["suffix"]

    return {"answer": final_answer}
