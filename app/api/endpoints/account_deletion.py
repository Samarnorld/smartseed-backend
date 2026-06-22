# app/api/endpoints/account_deletion.py
from __future__ import annotations
import logging
import app.core.firebase  # noqa: F401 — ensures Firebase Admin is initialized
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from firebase_admin import auth as fb_auth
from pydantic import BaseModel, Field
from app.core.limiter import limiter
from app.services.account_deletion import (
    build_confirmation_url,
    consume_deletion_token,
    mint_deletion_token,
    send_deletion_email,
)

router = APIRouter(tags=["Account"])
logger = logging.getLogger(__name__)

def verify_bearer(request: Request) -> dict:
    """Verify Firebase token from Authorization header with revocation check."""
    raw = request.headers.get("Authorization") or ""
    client_ip = request.client.host if request.client else "unknown"
    
    if not raw.startswith("Bearer "):
        logger.warning(f"Missing bearer token from {client_ip}")
        raise HTTPException(401, detail="Missing Authorization bearer token")
    
    id_token = raw.removeprefix("Bearer ").strip()
    if not id_token:
        logger.warning(f"Empty token from {client_ip}")
        raise HTTPException(401, detail="Missing token")
    
    try:
        return fb_auth.verify_id_token(id_token, check_revoked=True)
    except fb_auth.ExpiredIdTokenError:
        logger.warning(f"Expired token from {client_ip}")
        raise HTTPException(401, detail="Token expired")
    except fb_auth.RevokedIdTokenError:
        logger.warning(f"Revoked token attempted from {client_ip}")
        raise HTTPException(401, detail="Token revoked")
    except fb_auth.InvalidIdTokenError:
        logger.warning(f"Invalid token from {client_ip}")
        raise HTTPException(401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Token verification failed from {client_ip}: {type(e).__name__}")
        raise HTTPException(401, detail="Could not verify token")


class ConfirmBody(BaseModel):
    token: str = Field(
        ...,
        min_length=20,
        max_length=500
    )

@router.post("/users/me/delete-account/request", status_code=204)
@limiter.limit("5/hour")
def request_account_deletion(request: Request, user: dict = Depends(verify_bearer)) -> Response:
    """Request account deletion. Sends confirmation email. Requires authentication."""
    uid = user.get("uid")
    if not uid:
        logger.warning(f"Invalid token payload from {request.client.host if request.client else 'unknown'}")
        raise HTTPException(401, detail="Invalid token payload")

    email = (user.get("email") or "").strip()
    if not email:
        logger.warning(f"Delete request from user {uid} with no email")
        raise HTTPException(
            400,
            detail="Your account has no email on file; use a sign-in method that provides an email.",
        )

    try:
        token = mint_deletion_token(uid)
        confirm_url = build_confirmation_url(token)
        send_deletion_email(email, confirm_url)
        logger.info(f"Account deletion requested by user {uid}")
        return Response(status_code=204)
    except Exception as e:
        logger.error(f"Failed to send deletion email to {email}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to send confirmation email")


@router.post("/users/me/delete-account/confirm", status_code=204)
@limiter.limit("10/hour")
def confirm_account_deletion(request: Request, body: ConfirmBody) -> Response:
    """Confirm account deletion using token from email. Deletes user account."""
    try:
        uid = consume_deletion_token(body.token.strip())
    except Exception as e:
        client_ip = request.client.host if request.client else "unknown"
        logger.warning(f"Invalid deletion token from {client_ip}: {type(e).__name__}")
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired deletion token"
        )

    try:
        fb_auth.delete_user(uid)
        logger.warning(f"User account deleted: {uid}")
    except fb_auth.UserNotFoundError:
        # User already deleted, that's fine
        logger.info(f"Delete confirmation for already-deleted user: {uid}")
    except Exception as e:
        logger.error(f"Failed to delete user {uid}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete account")

    return Response(status_code=204)