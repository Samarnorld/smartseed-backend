# app/core/firebase.py
import firebase_admin
from firebase_admin import credentials, auth
import os
from pathlib import Path

service_account = os.getenv("FIREBASE_SERVICE_ACCOUNT")

if not service_account:
    raise RuntimeError("FIREBASE_SERVICE_ACCOUNT not found in environment")

if not firebase_admin._apps:
    cred = credentials.Certificate(Path(service_account))
    firebase_admin.initialize_app(cred)

def verify_token(id_token: str):
    return auth.verify_id_token(id_token)
