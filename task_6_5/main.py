import secrets
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from passlib.context import CryptContext
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import jwt

app = FastAPI(title="Task 6.5 - JWT with Rate Limiter")
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
limiter = Limiter(key_func=get_remote_address)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

SECRET_KEY = "your-secret-key-change-me"
ALGORITHM = "HS256"
EXPIRATION_MINUTES = 30


class User(BaseModel):
    username: str
    password: str


class UserInDB(BaseModel):
    username: str
    hashed_password: str


fake_users_db = {}


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_jwt_token(username: str) -> str:
    expiration = datetime.now(timezone.utc) + timedelta(minutes=EXPIRATION_MINUTES)
    payload = {"sub": username, "exp": expiration}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_jwt_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_jwt_token(token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    return username


@app.post("/register")
@limiter.limit("1/minute")
async def register(request: Request, user: User):
    if user.username in fake_users_db:
        raise HTTPException(status_code=409, detail="User already exists")

    hashed = hash_password(user.password)
    fake_users_db[user.username] = UserInDB(username=user.username, hashed_password=hashed)
    return {"message": "New user created"}


@app.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, user: User):
    db_user = fake_users_db.get(user.username)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not secrets.compare_digest(user.username, db_user.username):
        raise HTTPException(status_code=401, detail="Authorization failed")

    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Authorization failed")

    access_token = create_jwt_token(user.username)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/protected_resource")
async def protected_resource(current_user: str = Depends(get_current_user)):
    return {"message": "Access granted"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8005, reload=True)