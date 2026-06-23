from typing import Optional, Dict
from app.database.session import get_db_session
from app.database import crud


def load_health_context(user_id: str) -> Dict:
    """从数据库加载用户 EHR 健康档案，返回结构化 dict"""
    db = get_db_session()
    try:
        record = crud.get_health_record(db, user_id)
        if not record:
            return {}
        return {
            "age": record.age,
            "gender": record.gender,
            "conditions": record.conditions or [],
            "medications": record.medications or [],
            "allergies": record.allergies or [],
        }
    finally:
        db.close()


def format_health_context_for_prompt(health_context: Dict) -> str:
    """将健康上下文格式化为 prompt 片段"""
    if not health_context:
        return "（无健康档案）"
    lines = []
    if health_context.get("age"):
        lines.append(f"年龄：{health_context['age']} 岁")
    if health_context.get("gender"):
        lines.append(f"性别：{health_context['gender']}")
    if health_context.get("conditions"):
        lines.append(f"既往病史：{', '.join(health_context['conditions'])}")
    if health_context.get("medications"):
        lines.append(f"当前用药：{', '.join(health_context['medications'])}")
    if health_context.get("allergies"):
        lines.append(f"过敏史：{', '.join(health_context['allergies'])}")
    return "\n".join(lines) if lines else "（无有效健康数据）"
