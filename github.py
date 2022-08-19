import requests
import os

ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"


def get_token(code):
    resp = requests.post(
        ACCESS_TOKEN_URL,
        data={
            "client_id": os.getenv("GITHUB_CLIENT_ID"),
            "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
            "code": code,
        },
        headers={"Accept": "application/json"},
    )
    return resp.json()["access_token"]


def get_user(token):
    resp = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"token {token}"},
    )
    return resp.json()
