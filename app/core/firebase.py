# app/core/firebase.py

import firebase_admin
from firebase_admin import credentials, auth
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, "secrets", "firebase-admin.json")

if not os.path.exists(SERVICE_ACCOUNT_PATH):
    raise RuntimeError("Firebase service account file not found")

if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)

def verify_token(id_token: str):
    return auth.verify_id_token(id_token)