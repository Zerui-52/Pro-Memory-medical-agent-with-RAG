from typing import Dict, List
from app.database.session import get_db_session
from app.database import crud
from app.config import settings


def load_memory_context(user_id: str, session_id: str) -> Dict:
    db = get_db_session()
    try:
        turns = crud.get_recent_memory(db, user_id, session_id, limit=settings.MEMORY_MAX_TURNS)
        history = [{"role": t.role, "content": t.content} for t in turns]
        return {"history": history, "turn_count": len(history)}
    finally:
        db.close()


def save_memory_turn(
    user_id: str,
    session_id: str,
    question: str,
    answer: str,
    triage_level: str = None,
):
    db = get_db_session()
    try:
        crud.add_memory_turn(db, user_id, session_id, "user", question, triage_level)
        crud.add_memory_turn(db, user_id, session_id, "assistant", answer, triage_level)
    finally:
        db.close()


def format_memory_for_prompt(memory_context: Dict) -> str:
    history: List[Dict] = memory_context.get("history", [])
    if not history:
        return "（无历史对话）"
    lines = []
    for turn in history[-6:]:
        role_label = "用户" if turn["role"] == "user" else "助手"
        lines.append(f"{role_label}：{turn['content']}")
    return "\n".join(lines)
