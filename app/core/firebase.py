# app/core/firebase.py

import firebase_admin
from firebase_admin import credentials, auth
import os
import logging

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, "secrets", "firebase-admin.json")

if not os.path.exists(SERVICE_ACCOUNT_PATH):
    logger.error(f"Firebase service account file not found at {SERVICE_ACCOUNT_PATH}")
    raise RuntimeError("Firebase service account file not found")

if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)
    logger.info("Firebase Admin initialized successfully")

def verify_token(id_token: str):
    """
    Verify Firebase ID token with revocation check.
    Raises exception if token is invalid, expired, or revoked.
    """
    try:
        decoded = auth.verify_id_token(id_token, check_revoked=True)
        return decoded
    except auth.RevokedIdTokenError:
        logger.warning(f"Revoked token attempted")
        raise
    except auth.ExpiredIdTokenError:
        logger.debug(f"Expired token")
        raise
    except auth.InvalidIdTokenError:
        logger.debug(f"Invalid token")
        raise
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise