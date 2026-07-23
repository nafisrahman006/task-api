from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(title="Task API", version="1.0")

tasks = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Write report", "done": True},
    {"id": 3, "title": "Walk the dog", "done": False},
]
next_id = 4


class TaskCreate(BaseModel):
    title: str = ""


@app.exception_handler(HTTPException)
def http_error_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.get("/", tags=["meta"], summary="API info")
def root():
    """Describes this API and lists its main resource endpoints."""
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health", tags=["meta"], summary="Liveness check")
def health():
    """Used by uptime checks / orchestrators to confirm the server is alive."""
    return {"status": "ok"}


@app.get("/tasks", tags=["tasks"], summary="List all tasks")
def list_tasks():
    return tasks


@app.get("/tasks/{task_id}", tags=["tasks"], summary="Get a single task by id")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


@app.post("/tasks", status_code=201, tags=["tasks"], summary="Create a task")
def create_task(payload: TaskCreate):
    global next_id
    title = payload.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="title is required and cannot be empty")
    task = {"id": next_id, "title": title, "done": False}
    tasks.append(task)
    next_id += 1
    return task
