from fastapi import APIRouter
from app.graph.workflow import medical_graph

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/mermaid", summary="获取 LangGraph 工作流 Mermaid 图")
def get_mermaid_graph():
    graph = medical_graph.get_graph()
    mermaid_str = graph.draw_mermaid()
    return {"mermaid": mermaid_str}
