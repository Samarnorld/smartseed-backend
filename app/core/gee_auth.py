# app/core/gee_auth.py

import ee
import os
from google.oauth2 import service_account

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, "secrets", "gee-service-account.json")

def init_gee() -> None:

    if not os.path.exists(SERVICE_ACCOUNT_PATH):
        raise RuntimeError("GEE service account file not found")

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_PATH,
        scopes=["https://www.googleapis.com/auth/earthengine"]
    )

    ee.Initialize(credentials)
    print("Google Earth Engine initialized successfully")