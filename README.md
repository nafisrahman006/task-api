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
