from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
from app.graph.workflow import medical_graph
from app.database.session import get_db_session
from app.database import crud

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    user_id: str
    session_id: Optional[str] = None
    question: str


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    triage_level: Optional[str] = None
    policy_mode: Optional[str] = None
    confidence_score: Optional[float] = None
    need_clarify: bool = False
    guardrail_result: Optional[str] = None


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())

    # 确保用户存在
    db = get_db_session()
    try:
        crud.get_or_create_user(db, request.user_id)
    finally:
        db.close()

    # 构造初始 state
    initial_state = {
        "user_id": request.user_id,
        "session_id": session_id,
        "original_question": request.question,
        "merged_question": "",
        "retrieval_query": "",
        "session_state": "",
        "clarify_question": "",
        "clarify_answer": "",
        "need_health_data": False,
        "need_medical_knowledge": False,
        "health_context": {},
        "memory_context": {},
        "episodic_context": [],
        "rag_context": [],
        "guardrail_result": "",
        "guardrail_reason": "",
        "triage_level": "",
        "policy_mode": "",
        "semantic_score": 0.0,
        "coverage_score": 0.0,
        "confidence_score": 0.0,
        "need_clarify": False,
        "answer": "",
        "error_log": [],
    }

    try:
        final_state = await medical_graph.ainvoke(initial_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph execution failed: {str(e)}")

    response = ChatResponse(
        session_id=session_id,
        answer=final_state.get("answer", "抱歉，处理您的问题时出现了错误。"),
        triage_level=final_state.get("triage_level"),
        policy_mode=final_state.get("policy_mode"),
        confidence_score=final_state.get("confidence_score"),
        need_clarify=final_state.get("need_clarify", False),
        guardrail_result=final_state.get("guardrail_result"),
    )

    error_log = final_state.get("error_log", [])
    if error_log:
        return {
            "session_id": session_id,
            "answer": response.answer,
            "triage_level": response.triage_level,
            "policy_mode": response.policy_mode,
            "confidence_score": response.confidence_score,
            "need_clarify": response.need_clarify,
            "guardrail_result": response.guardrail_result,
            "error_log": error_log,
        }

    return response


@router.get("/health-record/{user_id}")
async def get_health_record(user_id: str):
    """查询用户健康档案（调试用）"""
    db = get_db_session()
    try:
        record = crud.get_health_record(db, user_id)
        if not record:
            return {"user_id": user_id, "record": None}
        return {
            "user_id": user_id,
            "record": {
                "age": record.age,
                "gender": record.gender,
                "conditions": record.conditions,
                "medications": record.medications,
                "allergies": record.allergies,
            },
        }
    finally:
        db.close()
