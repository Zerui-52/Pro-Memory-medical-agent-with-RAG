from sqlalchemy import Column, String, Text, Float, Boolean, DateTime, JSON, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime,timezone
import uuid

Base = declarative_base()


def gen_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=utc_now)


class HealthRecord(Base):
    """模拟 EHR 数据：存储用户健康档案"""
    __tablename__ = "health_records"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, nullable=False, index=True)
    age = Column(Float, nullable=True)
    gender = Column(String, nullable=True)
    conditions = Column(JSON, default=list)    # 既往病史列表
    medications = Column(JSON, default=list)   # 当前用药列表
    allergies = Column(JSON, default=list)     # 过敏史
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)


class ConversationMemory(Base):
    """对话历史记录"""
    __tablename__ = "conversation_memory"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, nullable=False, index=True)
    session_id = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False)       # "user" | "assistant"
    content = Column(Text, nullable=False)
    triage_level = Column(String, nullable=True)
    created_at = Column(DateTime, default=utc_now)


class ClarifyState(Base):
    """跨轮 Clarify 状态持久化"""
    __tablename__ = "clarify_states"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, nullable=False, index=True)
    session_id = Column(String, nullable=False, unique=True)
    pending_clarify = Column(Boolean, default=False)
    original_question = Column(Text, nullable=True)
    clarify_question = Column(Text, nullable=True)
    clarify_round = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
