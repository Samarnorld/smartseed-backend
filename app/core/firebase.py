# app/core/firebase.py
import firebase_admin
from firebase_admin import credentials, auth
import os
import json

service_account = os.getenv("FIREBASE_SERVICE_ACCOUNT")

if not service_account:
    raise RuntimeError("FIREBASE_SERVICE_ACCOUNT not found in environment")

# Initialize Firebase only once
if not firebase_admin._apps:
    cred_dict = json.loads(service_account)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

def verify_token(id_token: str):
    return auth.verify_id_token(id_token)

