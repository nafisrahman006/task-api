from fastapi import FastAPI

app = FastAPI(title="Task API", version="1.0")


@app.get("/", tags=["meta"], summary="API info")
def root():
    """Describes this API and lists its main resource endpoints."""
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health", tags=["meta"], summary="Liveness check")
def health():
    """Used by uptime checks / orchestrators to confirm the server is alive."""
    return {"status": "ok"}
