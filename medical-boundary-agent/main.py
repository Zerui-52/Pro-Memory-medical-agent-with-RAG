from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.chat import router as chat_router
from app.api.graph_api import router as graph_router
from app.database.session import init_db
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化数据库
    init_db()
    print(f"[OK] {settings.APP_NAME} started")
    yield
    print("[INFO] Shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    description="Medical Boundary Agent - LangGraph + RAG + SQL",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(chat_router, prefix="/api")
app.include_router(graph_router, prefix="/api")


@app.get("/")
def root():
    return {"status": "ok", "app": settings.APP_NAME}


@app.get("/health")
def health():
    return {"status": "healthy"}
