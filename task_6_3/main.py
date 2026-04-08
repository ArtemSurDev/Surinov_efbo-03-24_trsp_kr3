import os
import secrets
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from dotenv import load_dotenv

load_dotenv()

MODE = os.getenv("MODE", "DEV")
DOCS_USER = os.getenv("DOCS_USER", "admin")
DOCS_PASSWORD = os.getenv("DOCS_PASSWORD", "secret123")
security = HTTPBasic()
def auth_docs(credentials: HTTPBasicCredentials = Depends(security)):
    if MODE != "DEV":
        raise HTTPException(status_code=404, detail="Not Found")

    correct_username = secrets.compare_digest(credentials.username, DOCS_USER)
    correct_password = secrets.compare_digest(credentials.password, DOCS_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials
if MODE == "PROD":
    app = FastAPI(title="Task 6.3", docs_url=None, redoc_url=None, openapi_url=None)
else:
    app = FastAPI(title="Task 6.3", docs_url=None, redoc_url=None)
if MODE == "DEV":
    from fastapi.openapi.docs import get_swagger_ui_html
    @app.get("/docs", include_in_schema=False, dependencies=[Depends(auth_docs)])
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(openapi_url="/openapi.json", title="API Docs")


    @app.get("/openapi.json", include_in_schema=False, dependencies=[Depends(auth_docs)])
    async def custom_openapi_json():
        from fastapi.openapi.utils import get_openapi
        return get_openapi(title=app.title, version=app.version, routes=app.routes)

@app.get("/")
async def root():
    return {"mode": MODE, "docs_available": MODE == "DEV"}
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8003)