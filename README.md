# TodoApp

TodoApp is a REST API for managing user accounts and personal to-do items. It is
built with FastAPI and SQLAlchemy, uses SQLite by default, and protects API
operations with bearer tokens.

## Requirements

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/) for dependency management

## Get started

From the project directory, install the locked dependencies and start the
development server:

```powershell
uv sync
uv run uvicorn main:app --reload
```

The app is available at <http://127.0.0.1:8000>. FastAPI's interactive API
documentation is at <http://127.0.0.1:8000/docs> (ReDoc:
<http://127.0.0.1:8000/redoc>).

On startup, the app creates missing tables in the configured database. The
default database URL is `sqlite:///./todosapp.db`, so the local database file
is created in the working directory and is excluded from Git.

## Authentication

Create an account with `POST /auth/` using JSON:

```json
{
  "username": "jane",
  "email": "jane@example.com",
  "first_name": "Jane",
  "last_name": "Doe",
  "password": "choose-a-password",
  "role": "user",
  "phone_number": "555-0100"
}
```

Log in with `POST /auth/token` using form fields named `username` and
`password`. The response contains an `access_token` and `token_type`. For
protected routes, send the token in the Authorization header as specified by
the API's OpenAPI documentation. Tokens expire after 20 minutes.

## API endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/auth/` | Register a user |
| `POST` | `/auth/token` | Log in and obtain an access token |
| `GET` | `/todos` | List the authenticated user's to-dos |
| `GET` | `/todos/{todo_id}` | Get one of the authenticated user's to-dos |
| `POST` | `/todos/create_todo` | Create a to-do |
| `PUT` | `/todos/update_todo/{todo_id}` | Update one of the authenticated user's to-dos |
| `DELETE` | `/todos/delete_todo/{todo_id}` | Delete one of the authenticated user's to-dos |
| `GET` | `/user/profile` | Get the authenticated user's profile |
| `PUT` | `/user/update_password` | Change the authenticated user's password |
| `GET` | `/admin/todos` | List all to-dos (admin role required) |

To-do create and update requests accept JSON with `title` (1–100 characters),
`description` (3–100 characters), `priority` (an integer from 1 to 5), and
`completed` (a boolean, defaulting to `false`).

## Project layout

- `main.py` — creates the FastAPI application and registers routers
- `routers/` — authentication, user, to-do, and admin endpoints
- `model.py` and `database.py` — SQLAlchemy models and database setup
- `alembic/` and `alembic.ini` — database migration configuration
- `pyproject.toml` and `uv.lock` — project metadata and locked dependencies