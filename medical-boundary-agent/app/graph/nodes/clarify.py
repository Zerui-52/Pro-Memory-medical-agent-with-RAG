from app.graph.state import MedicalState
from app.services.llm_service import chat

CLARIFY_SYSTEM = "你是一个医疗健康助手，需要向用户追问以获取更准确的回答所需信息。"

CLARIFY_PROMPT = """用户问题：{question}

当前置信度较低（语义得分：{semantic:.2f}，覆盖率：{coverage:.2f}），
需要追问用户以获取更多信息。

请生成一个简洁、友好的追问句，帮助澄清以下方面（选最重要的一个）：
- 症状持续时间和严重程度
- 相关病史或用药情况
- 症状具体表现

只输出追问句本身，不超过40字。"""


def clarify_node(state: MedicalState) -> dict:
    """
    生成追问句。
    不进行回答，只生成 clarify_question，
    等待下轮用户输入后由 Clarify Context Check 合并。
    """
    prompt = CLARIFY_PROMPT.format(
        question=state["merged_question"],
        semantic=state.get("semantic_score", 0.0),
        coverage=state.get("coverage_score", 0.0),
    )

    clarify_question = chat(
        system=CLARIFY_SYSTEM,
        user=prompt,
        temperature=0.3,
        max_tokens=100,
    ).strip()

    return {
        "clarify_question": clarify_question,
        "answer": clarify_question,  # 本轮回复就是追问句
    }
