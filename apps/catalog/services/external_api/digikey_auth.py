import os
import requests
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[4]
load_dotenv(BASE_DIR / ".env")

CLIENT_ID = os.getenv("DIGIKEY_CLIENT_ID")
CLIENT_SECRET = os.getenv("DIGIKEY_CLIENT_SECRET")
ENV = os.getenv("DIGIKEY_ENV")

if ENV == "sandbox":
    TOKEN_URL = "https://sandbox-api.digikey.com/v1/oauth2/token"
else:
    TOKEN_URL = "https://api.digikey.com/v1/oauth2/token"


def get_access_token():
    response = requests.post(
        TOKEN_URL,
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "client_credentials",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if response.status_code != 200:
        raise Exception(response.text)

    return response.json()["access_token"]
