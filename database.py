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
