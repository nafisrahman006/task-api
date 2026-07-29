import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any


class TaskRepository:
    def __init__(self):
        self.conn_string = os.getenv("DATABASE_URL")
        if not self.conn_string:
            raise ValueError("DATABASE_URL environment variable is not set")

    def _get_conn(self):
        return psycopg2.connect(self.conn_string)

    def get_all(
        self,
        search: Optional[str] = None,
        done: Optional[bool] = None,
        sort: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = "SELECT id, title, done, created_at::text, updated_at::text FROM tasks WHERE 1=1"
        params = []

        if search:
            query += " AND title ILIKE %s"
            params.append(f"%{search}%")

        if done is not None:
            query += " AND done = %s"
            params.append(done)

        if sort == "title":
            query += " ORDER BY title ASC"
        else:
            query += " ORDER BY id ASC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [dict(row) for row in rows]

    def get_by_id(self, task_id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_conn()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "SELECT id, title, done, created_at::text, updated_at::text FROM tasks WHERE id = %s",
            (task_id,),
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return dict(row) if row else None

    def create(self, title: str) -> Dict[str, Any]:
        conn = self._get_conn()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "INSERT INTO tasks (title, done) VALUES (%s, FALSE) RETURNING id, title, done, created_at::text, updated_at::text",
            (title,),
        )
        row = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        return dict(row)

    def update(
        self, task_id: int, title: Optional[str] = None, done: Optional[bool] = None
    ) -> Dict[str, Any]:
        conn = self._get_conn()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        updates = []
        params = []

        if title is not None:
            updates.append("title = %s")
            params.append(title)

        if done is not None:
            updates.append("done = %s")
            params.append(done)

        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(task_id)

        sql = f"UPDATE tasks SET {', '.join(updates)} WHERE id = %s RETURNING id, title, done, created_at::text, updated_at::text"
        cursor.execute(sql, params)
        row = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        return dict(row)

    def delete(self, task_id: int) -> None:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        conn.commit()
        cursor.close()
        conn.close()

    def get_stats(self) -> Dict[str, int]:
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM tasks")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tasks WHERE done = TRUE")
        completed = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tasks WHERE done = FALSE")
        pending = cursor.fetchone()[0]

        cursor.close()
        conn.close()
        return {"total": total, "completed": completed, "pending": pending}