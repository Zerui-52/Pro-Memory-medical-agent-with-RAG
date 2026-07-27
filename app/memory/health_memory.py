from app.graph.state import MedicalState
from app.services.health_service import load_health_context
from app.vectorstore.health_index import index_health, search_health


def load_health(state: MedicalState) -> dict:
    if not state.get("need_health_data", False):
        return {}

    user_id = state["user_id"]
    record = load_health_context(user_id)

    if not record:
        return {}

    # 索引所有条目供 ANN 后续检索
    items = []
    for c in record.get("conditions", []):
        items.append({"category": "condition", "value": c})
    for m in record.get("medications", []):
        items.append({"category": "medication", "value": m})
    for a in record.get("allergies", []):
        items.append({"category": "allergy", "value": a})
    if items:
        index_health(user_id, items)

    # 用当前问题语义召回相关条目
    query = state.get("retrieval_query") or state["merged_question"]
    hits = search_health(query, user_id, top_k=5)

    filtered = dict(record)
    if hits:
        relevant_conditions = [h["text"] for h in hits if h["category"] == "condition"]
        relevant_medications = [h["text"] for h in hits if h["category"] == "medication"]
        relevant_allergies = [h["text"] for h in hits if h["category"] == "allergy"]
        if relevant_conditions:
            filtered["conditions"] = relevant_conditions
        if relevant_medications:
            filtered["medications"] = relevant_medications
        if relevant_allergies:
            filtered["allergies"] = relevant_allergies

    return filtered
