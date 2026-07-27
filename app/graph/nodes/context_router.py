from app.graph.state import MedicalState
from app.graph.state_machine import record_error
from app.services.llm_service import classify

ROUTE_PROMPT = """判断以下医疗问题需要哪些数据源。

问题：{question}

请回答以下两个问题（每行一个，格式严格为 yes 或 no）：
1. 是否需要用户个人健康档案（EHR）？（涉及"我的"病史、用药、过敏等个人化信息时选yes）
2. 是否需要检索医学知识库？（涉及疾病机制、药物信息、治疗方案等通用知识时选yes）

只输出两行，格式：
need_health: yes/no
need_knowledge: yes/no"""


def context_router_node(state: MedicalState) -> dict:
    """
    分析问题，决定 need_health_data 和 need_medical_knowledge。
    这两个布尔字段控制 Health Loader 和 Knowledge Retriever 是否按需执行。
    """
    question = state["merged_question"]
    prompt = ROUTE_PROMPT.format(question=question)
    error_updates = {}

    try:
        result = classify(prompt).lower()
        need_health = "need_health: yes" in result
        need_knowledge = "need_knowledge: yes" in result
    except Exception as e:
        need_health = True
        need_knowledge = True
        error_updates = record_error(state, "context_router", e)

    return {
        "need_health_data": need_health,
        "need_medical_knowledge": need_knowledge,
        **error_updates,
    }
