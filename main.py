import os
from pathlib import Path
from fastapi import FastAPI, UploadFile, Response, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from deta import Deta
from nanoid import generate

from AuthorizationDependencies import AuthorizeApiKeyDependency, AuthorizeDependency
from ValidateFileMiddleware import ValidateFileMiddleware
from github import get_token, get_user

deta = Deta(os.getenv("DETA_PROJECT_KEY"))
db = deta.Base("uploads")
users_db = deta.Base("users")
settings_db = deta.Base("settings")
drive = deta.Drive("uploads")

auth_apikey_dependency = AuthorizeApiKeyDependency(users_db)
auth_dependency = AuthorizeDependency()

pages = Jinja2Templates(directory="pages")
app = FastAPI(
    middleware=[
        Middleware(ValidateFileMiddleware),
        Middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET")),
    ]
)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/login")
async def login(request: Request):
    return pages.TemplateResponse(
        "index.html", {"request": request, "client_id": os.getenv("GITHUB_CLIENT_ID")}
    )


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login")


@app.get("/dashboard")
async def dashboard(request: Request, user: dict = Depends(auth_dependency)):
    return pages.TemplateResponse("dashboard.html", {"request": request, "user": user})


@app.get("/api/callback")
async def register(request: Request):
    code = request.query_params["code"]
    token = get_token(code)
    user = get_user(token)
    existing_user = users_db.fetch({"user_id": user["id"]})
    if existing_user.count == 0:
        if not settings_db.get("settings").get("allow_registration", False):
            return Response(content="Registration is disabled", status_code=403)
        api_key = generate(size=32)
        user_info = {
            "user_id": user["id"],
            "username": user["login"],
            "api_key": api_key,
        }
        new_user = users_db.insert(user_info)
        request.session["user"] = new_user
        return RedirectResponse(url="/dashboard")
    else:
        request.session["user"] = existing_user.items[0]
        return RedirectResponse(url="/dashboard")


@app.patch("/api/user/api_key")
async def regen_api_key(request: Request, user: dict = Depends(auth_dependency)):
    api_key = generate(size=32)
    users_db.update({"api_key": api_key}, user.get("key"))
    request.session["user"]["api_key"] = api_key
    return {"api_key": api_key}


@app.post("/api/file/upload/")
async def upload_file(file: UploadFile, user: dict = Depends(auth_apikey_dependency)):
    ext = Path(file.filename).suffix
    file_id = generate(size=10)
    file_name = drive.put(
        f"{file_id}{ext}",
        file.file,
        content_type=file.content_type,
    )
    file_data = {
        "key": file_id,
        "name": file_name,
        "type": file.content_type,
        "user_id": user.get("user_id"),
    }
    db.insert(file_data)
    return file_data


@app.get("/{file_id}")
async def get_file(file_id: str):
    file_info = db.get(file_id)
    if file_info is None:
        return {"error": "File not found"}
    file = drive.get(file_info["name"])
    return Response(file.read(), media_type=file_info["type"])
