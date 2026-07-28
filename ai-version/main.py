"""
Task API - A production-ready FastAPI to-do list manager.
Stages: 0 (Hello) → 1 (Root/Health) → 2 (Read/404) → 3 (Create/Validation)
      → 4 (Full CRUD) → 5 (Swagger Docs) → 6 (GitHub Publish)
"""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

app = FastAPI(
    title="Task API",
    description="A simple yet production-ready REST API for managing to-do tasks.",
    version="1.0.0",
)

# -----------------------------------------------------------------------------
# STAGE 2 — In-Memory Data Store (pre-filled with 3 tasks)
# -----------------------------------------------------------------------------
tasks_db: List[dict] = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Walk the dog", "done": False},
    {"id": 3, "title": "Read a book", "done": True},
]

# -----------------------------------------------------------------------------
# Pydantic Models (Validation & Serialization)
# -----------------------------------------------------------------------------
class Task(BaseModel):
    id: int
    title: str
    done: bool

    class Config:
        json_schema_extra = {
            "example": {"id": 1, "title": "Buy milk", "done": False}
        }


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Title of the task")

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

    class Config:
        json_schema_extra = {"example": {"title": "Buy milk"}}


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, description="New title for the task")
    done: Optional[bool] = Field(None, description="Completion status")

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip() if v is not None else v

    class Config:
        json_schema_extra = {"example": {"title": "Buy oat milk", "done": True}}


# -----------------------------------------------------------------------------
# STAGE 1 — Root and Health Endpoints
# -----------------------------------------------------------------------------
@app.get(
    "/",
    response_model=dict,
    summary="API Root",
    description="Returns basic API metadata and available endpoints.",
    tags=["Meta"],
)
def read_root() -> dict:
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"],
    }


@app.get(
    "/health",
    response_model=dict,
    summary="Health Check",
    description="Returns the health status of the API.",
    tags=["Meta"],
)
def health_check() -> dict:
    return {"status": "ok"}


# -----------------------------------------------------------------------------
# STAGE 2 & 4 — Read Endpoints
# -----------------------------------------------------------------------------
@app.get(
    "/tasks",
    response_model=List[Task],
    summary="List All Tasks",
    description="Retrieves the full list of tasks from the in-memory store.",
    tags=["Tasks"],
)
def list_tasks() -> List[dict]:
    return tasks_db


@app.get(
    "/tasks/{task_id}",
    response_model=Task,
    summary="Get a Single Task",
    description="Retrieves a specific task by its ID. Returns 404 if not found.",
    tags=["Tasks"],
)
def get_task(task_id: int) -> dict:
    for task in tasks_db:
        if task["id"] == task_id:
            return task
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found",
    )


# -----------------------------------------------------------------------------
# STAGE 3 — Create Endpoint
# -----------------------------------------------------------------------------
@app.post(
    "/tasks",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
    summary="Create a New Task",
    description="Creates a new task with an auto-assigned ID. Returns 400 if title is missing or empty.",
    tags=["Tasks"],
)
def create_task(payload: TaskCreate) -> dict:
    next_id = max((t["id"] for t in tasks_db), default=0) + 1
    new_task = {
        "id": next_id,
        "title": payload.title,
        "done": False,
    }
    tasks_db.append(new_task)
    return new_task


# -----------------------------------------------------------------------------
# STAGE 4 — Update Endpoint
# -----------------------------------------------------------------------------
@app.put(
    "/tasks/{task_id}",
    response_model=Task,
    summary="Update a Task",
    description="Replaces title and/or done status of an existing task. Returns 404 if ID not found, 400 if body invalid.",
    tags=["Tasks"],
)
def update_task(task_id: int, payload: TaskUpdate) -> dict:
    for task in tasks_db:
        if task["id"] == task_id:
            if payload.title is not None:
                task["title"] = payload.title
            if payload.done is not None:
                task["done"] = payload.done
            return task
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found",
    )


# -----------------------------------------------------------------------------
# STAGE 4 — Delete Endpoint
# -----------------------------------------------------------------------------
@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a Task",
    description="Removes a task by ID. Returns 204 on success, 404 if not found.",
    tags=["Tasks"],
)
def delete_task(task_id: int) -> None:
    for idx, task in enumerate(tasks_db):
        if task["id"] == task_id:
            tasks_db.pop(idx)
            return
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found",
    )