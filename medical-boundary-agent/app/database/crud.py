from sqlalchemy.orm import Session
from typing import Optional, List
from app.database.models import User, HealthRecord, ConversationMemory, ClarifyState
from datetime import datetime


# ── User ──────────────────────────────────────────────

def get_or_create_user(db: Session, user_id: str) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(id=user_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


# ── HealthRecord ──────────────────────────────────────

def get_health_record(db: Session, user_id: str) -> Optional[HealthRecord]:
    return db.query(HealthRecord).filter(HealthRecord.user_id == user_id).first()


def upsert_health_record(db: Session, user_id: str, data: dict) -> HealthRecord:
    record = get_health_record(db, user_id)
    if not record:
        record = HealthRecord(user_id=user_id, **data)
        db.add(record)
    else:
        for key, val in data.items():
            setattr(record, key, val)
        record.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(record)
    return record


# ── ConversationMemory ────────────────────────────────

def add_memory_turn(
    db: Session,
    user_id: str,
    session_id: str,
    role: str,
    content: str,
    triage_level: Optional[str] = None,
) -> ConversationMemory:
    turn = ConversationMemory(
        user_id=user_id,
        session_id=session_id,
        role=role,
        content=content,
        triage_level=triage_level,
    )
    db.add(turn)
    db.commit()
    db.refresh(turn)
    return turn


def get_recent_memory(
    db: Session, user_id: str, session_id: str, limit: int = 10
) -> List[ConversationMemory]:
    return (
        db.query(ConversationMemory)
        .filter(
            ConversationMemory.user_id == user_id,
            ConversationMemory.session_id == session_id,
        )
        .order_by(ConversationMemory.created_at.desc())
        .limit(limit)
        .all()[::-1]  # 时间正序返回
    )


# ── ClarifyState ──────────────────────────────────────

def get_clarify_state(db: Session, session_id: str) -> Optional[ClarifyState]:
    return db.query(ClarifyState).filter(ClarifyState.session_id == session_id).first()


def save_clarify_state(
    db: Session,
    user_id: str,
    session_id: str,
    pending: bool,
    original_question: Optional[str] = None,
    clarify_question: Optional[str] = None,
    clarify_round: Optional[int] = None,
) -> ClarifyState:
    state = get_clarify_state(db, session_id)
    if not state:
        state = ClarifyState(
            user_id=user_id,
            session_id=session_id,
            pending_clarify=pending,
            original_question=original_question,
            clarify_question=clarify_question,
        )
        db.add(state)
    else:
        state.pending_clarify = pending
        state.original_question = original_question
        state.clarify_question = clarify_question
        state.updated_at = datetime.utcnow()
    if clarify_round is not None:
        state.clarify_round = clarify_round
    db.commit()
    db.refresh(state)
    return state


def clear_clarify_state(db: Session, session_id: str):
    state = get_clarify_state(db, session_id)
    if state:
        state.pending_clarify = False
        state.original_question = None
        state.clarify_question = None
        state.updated_at = datetime.utcnow()
        db.commit()


def reset_clarify_round(db: Session, session_id: str):
    state = get_clarify_state(db, session_id)
    if state:
        state.clarify_round = 0
        db.commit()
