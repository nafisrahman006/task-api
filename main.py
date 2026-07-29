from fastapi import FastAPI, HTTPException, Query, Response
from pydantic import BaseModel
from typing import Optional
from repository import TaskRepository

app = FastAPI(title="Task API")
repo = TaskRepository()


class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


@app.get("/")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks")
def get_tasks(
    search: Optional[str] = Query(None, description="Search in title"),
    done: Optional[bool] = Query(None, description="Filter by done status"),
    sort: Optional[str] = Query(None, description="Use 'title' to sort alphabetically"),
):
    return repo.get_all(search=search, done=done, sort=sort)


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = repo.get_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.get("/stats")
def get_stats():
    return repo.get_stats()


@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")
    return repo.create(task.title)


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    if task.title is None and task.done is None:
        raise HTTPException(status_code=400, detail="Provide at least one field to update")

    existing = repo.get_by_id(task_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.title is not None and not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    return repo.update(task_id, task.title, task.done)


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    existing = repo.get_by_id(task_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Task not found")
    repo.delete(task_id)
    return Response(status_code=204)