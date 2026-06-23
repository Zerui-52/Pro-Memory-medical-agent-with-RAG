from app.graph.state import MedicalState
from app.database.session import get_db_session
from app.database import crud


def save_clarify_state_node(state: MedicalState) -> dict:
    db = get_db_session()
    try:
        cs = crud.get_clarify_state(db, state["session_id"])
        current_round = (cs.clarify_round if cs else 0) + 1
        crud.save_clarify_state(
            db=db,
            user_id=state["user_id"],
            session_id=state["session_id"],
            pending=True,
            original_question=state.get("merged_question", ""),
            clarify_question=state.get("clarify_question", ""),
            clarify_round=current_round,
        )
    finally:
        db.close()

    return {"session_state": "clarifying"}
