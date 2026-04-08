from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from passlib.context import CryptContext
import secrets

app = FastAPI(title="Task 6.2 - Password Hashing")
security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserBase(BaseModel):
    username: str


class User(UserBase):
    password: str


class UserInDB(UserBase):
    hashed_password: str


fake_users_db = {}


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def auth_user(credentials: HTTPBasicCredentials = Depends(security)):
    user = fake_users_db.get(credentials.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    if not secrets.compare_digest(credentials.username, user.username):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return user


@app.post("/register")
async def register(user: User):
    if user.username in fake_users_db:
        raise HTTPException(status_code=409, detail="User already exists")

    hashed = hash_password(user.password)
    fake_users_db[user.username] = UserInDB(username=user.username, hashed_password=hashed)
    return {"message": f"User {user.username} registered successfully!"}


@app.get("/login")
async def login(user: UserInDB = Depends(auth_user)):
    return {"message": f"Welcome, {user.username}!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8002)