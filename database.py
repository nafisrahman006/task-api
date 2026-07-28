from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI(title="Task API")


# ----------------------------
# Database Connection
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
            done BOOLEAN NOT NULL
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
    title: str
    done: bool

# ----------------------------
# GET ALL TASKS
# ----------------------------

@app.get("/tasks")
def get_tasks():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "id": row["id"],
            "title": row["title"],
            "done": bool(row["done"]),
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

    cursor.execute(
        "SELECT * FROM tasks WHERE id=?",
        (task_id,),
    )

    row = cursor.fetchone()

    conn.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
    }
# ----------------------------
# CREATE TASK
# ----------------------------

@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):

    if not task.title.strip():
        raise HTTPException(
            status_code=400,
            detail="Title is required",
        )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO tasks(title, done) VALUES(?, ?)",
        (task.title, False),
    )

    conn.commit()

    task_id = cursor.lastrowid

    conn.close()

    return {
        "id": task_id,
        "title": task.title,
        "done": False,
    }


# ----------------------------
# UPDATE TASK
# ----------------------------

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM tasks WHERE id=?",
        (task_id,),
    )

    if cursor.fetchone() is None:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    cursor.execute(
        """
        UPDATE tasks
        SET title=?, done=?
        WHERE id=?
        """,
        (task.title, task.done, task_id),
    )

    conn.commit()
    conn.close()

    return {
        "id": task_id,
        "title": task.title,
        "done": task.done,
    }
