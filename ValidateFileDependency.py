import mimetypes
from fastapi import Request, HTTPException
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


class ValidateFileDependency:
    async def __call__(self, request: Request):
        # file name validation
        file_name = request.query_params.get("file_name")
        if not file_name:
            raise HTTPException(status_code=400, detail="file_name is required")
        file_extention = Path(file_name).suffix
        if file_extention in BANNED_EXTENTIONS:
            raise HTTPException(status_code=400, detail="File extension is not allowed")

        # file content validation
        file_contents = await request.body()
        if not file_contents:
            raise HTTPException(status_code=400, detail="No file found")
        if len(file_contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File is too big")
        return {
            "file_extention": file_extention,
            "content_type": mimetypes.guess_type(file_name)[0],
            "file_contents": file_contents,
        }
