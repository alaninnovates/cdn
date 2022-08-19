from fastapi import Header, HTTPException, Request
from deta.base import _Base


class AuthorizeApiKeyDependency:
    def __init__(self, users_db: _Base):
        self.users_db = users_db

    def __call__(self, x_api_key: str = Header(...)):
        user = self.users_db.fetch({"api_key": x_api_key})
        if user.count == 0:
            raise HTTPException(status_code=401, detail="Unauthorized")

        return user.items[0]


class AuthorizeDependency:
    def __call__(self, request: Request):
        user = request.session.get("user")
        if user is None:
            raise HTTPException(status_code=401, detail="Unauthorized")
        return user
