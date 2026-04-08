from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, Set, List
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from passlib.context import CryptContext
import jwt

app = FastAPI(title="Task 7.1 - RBAC")
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "your-secret-key-change-me"
ALGORITHM = "HS256"
EXPIRATION_MINUTES = 30


class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class Permission:
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"


class User(BaseModel):
    username: str
    password: str


class UserInDB(BaseModel):
    username: str
    hashed_password: str


fake_users_db = {}
user_roles: Dict[str, Role] = {}

role_permissions: Dict[Role, Set[str]] = {
    Role.ADMIN: {Permission.CREATE, Permission.READ, Permission.UPDATE, Permission.DELETE},
    Role.USER: {Permission.READ, Permission.UPDATE},
    Role.GUEST: {Permission.READ},
}


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
    user = fake_users_db.get(username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def get_user_role(username: str) -> Role:
    return user_roles.get(username, Role.GUEST)


def set_user_role(username: str, role: Role):
    if username in fake_users_db:
        user_roles[username] = role
        return True
    return False


def require_role(required_roles: List[Role]):
    async def role_checker(current_user=Depends(get_current_user)):
        user_role = get_user_role(current_user.username)
        if user_role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in required_roles]}, your role: {user_role.value}"
            )
        return current_user

    return role_checker


def require_permission(required_permission: str):
    async def permission_checker(current_user=Depends(get_current_user)):
        user_role = get_user_role(current_user.username)
        permissions = role_permissions.get(user_role, set())
        if required_permission not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required permission: {required_permission}"
            )
        return current_user

    return permission_checker


@app.post("/register")
async def register(user: User):
    if user.username in fake_users_db:
        raise HTTPException(status_code=409, detail="User already exists")

    hashed = hash_password(user.password)
    fake_users_db[user.username] = UserInDB(username=user.username, hashed_password=hashed)
    set_user_role(user.username, Role.USER)
    return {"message": "New user created"}


@app.post("/login")
async def login(user: User):
    db_user = fake_users_db.get(user.username)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Authorization failed")

    access_token = create_jwt_token(user.username)
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/admin/set_role/{username}")
async def assign_role(username: str, role: Role, admin=Depends(require_role([Role.ADMIN]))):
    if set_user_role(username, role):
        return {"message": f"Role {role.value} assigned to {username}"}
    raise HTTPException(status_code=404, detail="User not found")


@app.post("/admin/resource")
async def admin_create_resource(current_user=Depends(require_role([Role.ADMIN]))):
    return {"message": f"Resource created by admin: {current_user.username}"}


@app.get("/user/resource")
async def user_read_resource(current_user=Depends(require_permission(Permission.READ))):
    return {"message": f"Resource read by: {current_user.username}"}


@app.put("/user/resource/{resource_id}")
async def user_update_resource(resource_id: int, current_user=Depends(require_permission(Permission.UPDATE))):
    return {"message": f"Resource {resource_id} updated by: {current_user.username}"}


@app.delete("/admin/resource/{resource_id}")
async def admin_delete_resource(resource_id: int, current_user=Depends(require_role([Role.ADMIN]))):
    return {"message": f"Resource {resource_id} deleted by admin: {current_user.username}"}


@app.get("/guest/resource")
async def guest_read_resource(current_user=Depends(get_current_user)):
    return {"message": f"Access granted for: {current_user.username}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8007)