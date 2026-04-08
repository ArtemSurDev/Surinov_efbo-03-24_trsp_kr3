import sqlite3
from contextlib import contextmanager
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Task 8.2 - Todo CRUD")
DATABASE_NAME = "todos.db"


@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_database():
    with get_db_connection() as conn:
        conn.execute("""
                     CREATE TABLE IF NOT EXISTS todos
                     (
                         id
                         INTEGER
                         PRIMARY
                         KEY
                         AUTOINCREMENT,
                         title
                         TEXT
                         NOT
                         NULL,
                         description
                         TEXT
                         NOT
                         NULL,
                         completed
                         BOOLEAN
                         DEFAULT
                         0
                     )
                     """)
        conn.commit()


init_database()


class TodoCreate(BaseModel):
    title: str
    description: str


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool


@app.post("/todos", response_model=TodoResponse, status_code=201)
async def create_todo(todo: TodoCreate):
    with get_db_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO todos (title, description) VALUES (?, ?)",
            (todo.title, todo.description)
        )
        conn.commit()
        todo_id = cursor.lastrowid
        row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()

    return TodoResponse(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        completed=bool(row["completed"])
    )


@app.get("/todos/{todo_id}", response_model=TodoResponse)
async def get_todo(todo_id: int):
    with get_db_connection() as conn:
        row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Todo not found")

    return TodoResponse(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        completed=bool(row["completed"])
    )


@app.get("/todos", response_model=List[TodoResponse])
async def list_todos():
    with get_db_connection() as conn:
        rows = conn.execute("SELECT * FROM todos").fetchall()

    return [
        TodoResponse(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            completed=bool(row["completed"])
        )
        for row in rows
    ]


@app.put("/todos/{todo_id}", response_model=TodoResponse)
async def update_todo(todo_id: int, todo_update: TodoUpdate):
    with get_db_connection() as conn:
        current = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
        if not current:
            raise HTTPException(status_code=404, detail="Todo not found")

        new_title = todo_update.title if todo_update.title is not None else current["title"]
        new_description = todo_update.description if todo_update.description is not None else current["description"]
        new_completed = todo_update.completed if todo_update.completed is not None else current["completed"]

        conn.execute(
            "UPDATE todos SET title = ?, description = ?, completed = ? WHERE id = ?",
            (new_title, new_description, new_completed, todo_id)
        )
        conn.commit()

        row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()

    return TodoResponse(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        completed=bool(row["completed"])
    )


@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    with get_db_connection() as conn:
        cursor = conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Todo not found")

    return {"message": "Todo deleted successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8009)