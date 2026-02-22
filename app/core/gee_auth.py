# app/core/gee_auth.py
import ee
import os
import json
from google.oauth2 import service_account


def init_gee() -> None:
    """
    Initialize Google Earth Engine using a service account JSON
    stored in an environment variable.
    """

    raw_json = os.getenv("GEE_SERVICE_ACCOUNT")

    if not raw_json:
        raise RuntimeError("GEE_SERVICE_ACCOUNT environment variable is missing")

    try:
        info = json.loads(raw_json)
    except json.JSONDecodeError:
        raise RuntimeError("GEE_SERVICE_ACCOUNT is not valid JSON")

    credentials = service_account.Credentials.from_service_account_info(
        info,
        scopes=["https://www.googleapis.com/auth/earthengine"]
    )

    ee.Initialize(credentials, project=info.get("project_id"))
    print("Google Earth Engine initialized successfully")
