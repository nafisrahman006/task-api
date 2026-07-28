# Task API

A small in-memory to-do list API built with **FastAPI**. It supports the
four CRUD operations on tasks (create, read, update, delete), self-documents
via Swagger UI, and validates input before trusting it.

Built stage by stage as a learning exercise — each commit corresponds to one
stage.

## Install & run

```bash
git clone https://github.com/nafisrahman006/task-api.git
cd task-api
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

The API is now live at `http://localhost:8000`, and interactive docs are at
`http://localhost:8000/docs`.

## Endpoints

| Method | Path           | Description                          | Success | Errors |
|--------|----------------|---------------------------------------|---------|--------|
| GET    | `/`            | API info (name, version, endpoints)   | 200     | —      |
| GET    | `/health`      | Liveness check                        | 200     | —      |
| GET    | `/tasks`       | List all tasks                        | 200     | —      |
| GET    | `/tasks/{id}`  | Get one task                          | 200     | 404    |
| POST   | `/tasks`       | Create a task (`{"title": "..."}`)    | 201     | 400    |
| PUT    | `/tasks/{id}`  | Update `title` and/or `done`          | 200     | 400, 404 |
| DELETE | `/tasks/{id}`  | Delete a task                         | 204     | 404    |

A task looks like: `{"id": 1, "title": "Buy milk", "done": false}`.

Errors are always returned as `{"error": "<message>"}` with the matching
HTTP status code — never a silent empty 200.

## Example

```
$ curl -i http://localhost:8000/tasks/1

HTTP/1.1 200 OK
content-type: application/json

{"id":1,"title":"Buy milk","done":false}
```

## Swagger UI

`/docs` is generated automatically by FastAPI from the code — every route
above shows up there with a **Try it out** button that fires real requests,
no `curl` needed.

![/docs](Screenshots/swagger_ui.png)
*(screenshot of `/docs` goes here)*

## Notes on state

Tasks live in an in-memory Python list — there's no database. Restarting
the server resets the task list back to the three seed tasks; anything
created, updated, or deleted during a session is lost. That's the
trade-off of Stage 0–6: it's the simplest possible storage, and it's why a
real backend eventually needs a persistent database.




# Task API — Week 2 · Assignment 2

A lightweight REST API for managing tasks, built with **FastAPI** and backed by **SQLite**. This project replaces the in-memory storage from Assignment 1 with a real database, demonstrating that persistence is an implementation detail — the API itself stays exactly the same.

---

## Why SQLite was chosen

SQLite was chosen because it is a **zero-configuration, serverless database** that stores all data in a single file. This makes it ideal for learning and small projects:

- No separate database server to install or run
- The database file (`tasks.db`) is created automatically on first run
- Data survives server restarts
- Moving to PostgreSQL or MySQL later only requires changing the connection layer — the SQL queries and API remain largely identical

---

## Database file location

The database file is stored in the project root:

```
project-root/
├── main.py
├── database.py
├── requirements.txt
├── README.md
└── tasks.db          ← SQLite database file (auto-created)
```

> **Note:** `tasks.db` is created automatically when you start the server for the first time. You do not need to create it manually.

---

## How to start the project

### 1. Clone the repository

```bash
git clone https://github.com/nafisrahman006/task-api.git
cd YOUR_REPO_NAME
```

### 2. Create a virtual environment (optional but recommended)

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the server

```bash
uvicorn database:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

Interactive documentation (Swagger UI) is available at:

```
http://127.0.0.1:8000/docs
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/health` | Health check |
| GET | `/tasks` | List all tasks (supports search, filter, sort) |
| GET | `/tasks/{id}` | Get a single task |
| POST | `/tasks` | Create a new task |
| PUT | `/tasks/{id}` | Update a task |
| DELETE | `/tasks/{id}` | Delete a task |
| GET | `/stats` | Return task statistics |

### Query parameters for `GET /tasks`

| Parameter | Type | Description |
|-----------|------|-------------|
| `search` | string | Search titles using SQL `LIKE` (e.g., `?search=milk`) |
| `done` | boolean | Filter by status (`?done=true` or `?done=false`) |
| `sort` | string | Sort alphabetically by title (`?sort=title`) |

---

## Example SQL queries executed

During development, the database was explored directly using **DB Browser for SQLite**. Below is one example query:

```sql
-- Count all tasks
SELECT COUNT(*) FROM tasks;
```

Other queries executed:

```sql
-- List every task
SELECT * FROM tasks;

-- Show only completed tasks
SELECT * FROM tasks WHERE done = 1;

-- Mark every task as completed
UPDATE tasks SET done = 1;

-- Delete all completed tasks
DELETE FROM tasks WHERE done = 1;
```

Modifying the database manually through DB Browser and then calling the API immediately reflected those changes, confirming that the API reads directly from the database.

---

## Database viewer screenshot

Below is a screenshot of the `tasks` table opened in **DB Browser for SQLite**:

![Database Viewer Screenshot](Screenshots/sqlite.png)

