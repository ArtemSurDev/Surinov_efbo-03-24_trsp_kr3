import sqlite3
from contextlib import contextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Task 8.1 - SQLite Registration")
DATABASE_NAME = "users.db"


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
                     CREATE TABLE IF NOT EXISTS users
                     (
                         id
                         INTEGER
                         PRIMARY
                         KEY
                         AUTOINCREMENT,
                         username
                         TEXT
                         NOT
                         NULL
                         UNIQUE,
                         password
                         TEXT
                         NOT
                         NULL
                     )
                     """)
        conn.commit()


init_database()


class User(BaseModel):
    username: str
    password: str


@app.post("/register")
async def register(user: User):
    with get_db_connection() as conn:
        existing = conn.execute(
            "SELECT id FROM users WHERE username = ?", (user.username,)
        ).fetchone()

        if existing:
            raise HTTPException(status_code=409, detail="User already exists")

        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (user.username, user.password)
        )
        conn.commit()

    return {"message": "User registered successfully!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8008)