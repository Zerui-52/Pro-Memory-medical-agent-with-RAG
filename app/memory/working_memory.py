from app.graph.state import MedicalState
from app.services.memory_service import load_memory_context


def load_working_memory(state):
    return load_memory_context(
        state["user_id"],
        state["session_id"],
    )
