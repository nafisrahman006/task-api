from fastapi import FastAPI, HTTPException, Query, Response
from pydantic import BaseModel
from typing import Optional
import sqlite3

app = FastAPI(title="Task API")

# ----------------------------
# Database
# ----------------------------

def get_connection():
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            [
                ("Buy milk", False),
                ("Write report", False),
                ("Walk the dog", True),
            ],
        )

    conn.commit()
    conn.close()


@app.on_event("startup")
def startup():
    init_db()


# ----------------------------
# Models
# ----------------------------

class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


# ----------------------------
# GET ALL TASKS (+ search, filter, sort)
# ----------------------------

@app.get("/tasks")
def get_tasks(
    search: Optional[str] = Query(None, description="Search in title"),
    done: Optional[bool] = Query(None, description="Filter by done status"),
    sort: Optional[str] = Query(None, description="Use 'title' to sort alphabetically"),
):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    if search:
        query += " AND title LIKE ?"
        params.append(f"%{search}%")

    if done is not None:
        query += " AND done = ?"
        params.append(1 if done else 0)

    if sort == "title":
        query += " ORDER BY title ASC"
    else:
        query += " ORDER BY id ASC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row["id"],
            "title": row["title"],
            "done": bool(row["done"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }
        for row in rows
    ]


# ----------------------------
# GET TASK BY ID
# ----------------------------

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


# ----------------------------
# STATS
# ----------------------------

@app.get("/stats")
def get_stats():
    conn = get_connection()
    cursor = conn.cursor()

    total = cursor.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    completed = cursor.execute("SELECT COUNT(*) FROM tasks WHERE done = 1").fetchone()[0]
    pending = cursor.execute("SELECT COUNT(*) FROM tasks WHERE done = 0").fetchone()[0]

    conn.close()

    return {"total": total, "completed": completed, "pending": pending}


# ----------------------------
# CREATE TASK
# ----------------------------

@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (task.title, False),
    )

    conn.commit()
    task_id = cursor.lastrowid
    conn.close()

    return get_task(task_id)


# ----------------------------
# UPDATE TASK
# ----------------------------

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    if task.title is None and task.done is None:
        raise HTTPException(status_code=400, detail="Provide at least one field to update")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    if cursor.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")

    updates = []
    params = []

    if task.title is not None:
        if not task.title.strip():
            conn.close()
            raise HTTPException(status_code=400, detail="Title cannot be empty")
        updates.append("title = ?")
        params.append(task.title)

    if task.done is not None:
        updates.append("done = ?")
        params.append(1 if task.done else 0)

    # Always bump updated_at
    updates.append("updated_at = CURRENT_TIMESTAMP")

    params.append(task_id)
    sql = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"

    cursor.execute(sql, params)
    conn.commit()
    conn.close()

    return get_task(task_id)


# ----------------------------
# DELETE TASK
# ----------------------------

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    if cursor.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")

    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

    return Response(status_code=204)