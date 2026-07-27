import traceback
from typing import Optional


def record_error(state: dict, node: str, error: Exception, detail: str = "") -> dict:
    """记录节点运行时错误到 error_log，返回增量更新"""
    entry = {
        "node": node,
        "error": str(error),
        "detail": detail,
    }
    log = list(state.get("error_log", []))
    log.append(entry)
    return {"error_log": log}
