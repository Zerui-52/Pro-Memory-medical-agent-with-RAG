from app.graph.state import MedicalState
from app.services.memory_service import save_memory_turn


def memory_update_node(state: MedicalState) -> dict:
    save_memory_turn(
        user_id=state["user_id"],
        session_id=state["session_id"],
        question=state["merged_question"],
        answer=state.get("answer", ""),
        triage_level=state.get("triage_level"),
    )
    return {"memory_context": state.get("memory_context", {}),
            "session_state": "active"}
