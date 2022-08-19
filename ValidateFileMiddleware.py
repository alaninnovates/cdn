from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from pathlib import Path

BANNED_EXTENTIONS = [
    ".jar",
    ".exe",
    ".exec",
    ".msi",
    ".com",
    ".bat",
    ".cmd",
    ".nt",
    ".scr",
    ".ps1",
    ".psm1",
    ".sh",
    ".bash",
    ".bsh",
    ".csh",
    ".bash_profile",
    ".bashrc",
    ".profile",
]
MAX_FILE_SIZE = 10 * 1024 * 1024


class ValidateFileMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.scope["path"] not in "/api/file/upload" or request.method != "POST":
            return await call_next(request)
        headers = request.headers
        if "content-length" not in headers:
            return JSONResponse(
                {"error": "Missing content-length header"}, status_code=400
            )
        if int(headers["content-length"]) > MAX_FILE_SIZE:
            return JSONResponse({"error": "File is too big"}, status_code=400)
        file = (await request.form()).get("file")
        if not await file.read(1):
            return JSONResponse({"error": "Missing file"}, status_code=400)
        ext = Path(file.filename).suffix
        if ext in BANNED_EXTENTIONS:
            return JSONResponse({"error": "File extension is banned"}, status_code=400)
        return await call_next(request)
