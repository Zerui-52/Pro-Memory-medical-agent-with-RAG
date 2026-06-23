from app.graph.state import MedicalState
from app.graph.state_machine import record_error
from app.database.session import get_db_session
from app.database import crud
from app.services.llm_service import classify

CLASSIFY_PROMPT = """你需要判断用户消息属于哪种类型：

FOLLOWUP：用户在回答上一轮的追问
NEW_QUESTION：用户开启了一个新的医疗问题

上一轮追问：{clarify_question}
用户当前消息：{user_input}

只输出一个词：FOLLOWUP 或 NEW_QUESTION"""


def message_router_node(state: MedicalState) -> dict:
    db = get_db_session()
    try:
        cs = crud.get_clarify_state(db, state["session_id"])
        pending = cs.pending_clarify if cs else False
        clarify_q = cs.clarify_question if cs else ""
        original = cs.original_question if cs else ""
    finally:
        db.close()

    if not pending:
        return {
            "session_state": "active",
            "clarify_answer": "",
            "merged_question": state["original_question"],
            "retrieval_query": state["original_question"],
        }

    user_input = state["original_question"]
    error_updates = {}

    try:
        result = classify(CLASSIFY_PROMPT.format(
            clarify_question=clarify_q,
            user_input=user_input,
        ))
        is_followup = "FOLLOWUP" in result.upper()
    except Exception as e:
        is_followup = True
        error_updates = record_error(state, "message_router", e)

    db = get_db_session()
    try:
        if is_followup:
            merged = (
                f"{original}\n"
                f"（补充信息 - 针对追问「{clarify_q}」的回答：{user_input}）"
            )
            crud.clear_clarify_state(db, state["session_id"])
            return {
                "session_state": "active",
                "clarify_answer": user_input,
                "merged_question": merged,
                "retrieval_query": merged,
                **error_updates,
            }
        else:
            crud.clear_clarify_state(db, state["session_id"])
            crud.reset_clarify_round(db, state["session_id"])
            return {
                "session_state": "active",
                "clarify_answer": "",
                "merged_question": user_input,
                "retrieval_query": user_input,
                **error_updates,
            }
    finally:
        db.close()
