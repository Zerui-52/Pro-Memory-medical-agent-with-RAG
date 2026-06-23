import subprocess, sys, os

log = open("uvicorn.log", "w", encoding="utf-8")
p = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
    cwd=os.path.dirname(os.path.abspath(__file__)),
    stdout=log,
    stderr=subprocess.STDOUT,
    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
)
print(f"PID: {p.pid}")
log.close()
