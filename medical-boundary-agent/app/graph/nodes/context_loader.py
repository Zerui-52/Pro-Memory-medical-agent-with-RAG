from app.graph.state import MedicalState
from app.memory.health_memory import load_health
from app.memory.working_memory import load_working_memory


def context_loader_node(state: MedicalState) -> dict:
    return {
        "health_context": load_health(state),
        "memory_context": load_working_memory(state),
    }