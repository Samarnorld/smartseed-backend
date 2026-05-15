from __future__ import annotations

import app.core.firebase  # noqa: F401 — ensures Firebase Admin is initialized
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from firebase_admin import auth as fb_auth
from pydantic import BaseModel

from app.services.account_deletion import (
    build_confirmation_url,
    consume_deletion_token,
    mint_deletion_token,
    send_deletion_email,
)

router = APIRouter(tags=["Account"])


def verify_bearer(request: Request) -> dict:
    raw = request.headers.get("Authorization") or ""
    if not raw.startswith("Bearer "):
        raise HTTPException(401, detail="Missing Authorization bearer token")
    id_token = raw.removeprefix("Bearer ").strip()
    if not id_token:
        raise HTTPException(401, detail="Missing token")
    try:
        return fb_auth.verify_id_token(id_token, check_revoked=True)
    except fb_auth.ExpiredIdTokenError:
        raise HTTPException(401, detail="Token expired")
    except fb_auth.RevokedIdTokenError:
        raise HTTPException(401, detail="Token revoked")
    except fb_auth.InvalidIdTokenError:
        raise HTTPException(401, detail="Invalid token")
    except Exception:
        raise HTTPException(401, detail="Could not verify token")


class ConfirmBody(BaseModel):
    token: str


@router.post("/users/me/delete-account/request", status_code=204)
def request_account_deletion(user: dict = Depends(verify_bearer)) -> Response:
    uid = user.get("uid")
    if not uid:
        raise HTTPException(401, detail="Invalid token payload")

    email = (user.get("email") or "").strip()
    if not email:
        raise HTTPException(
            400,
            detail="Your account has no email on file; use a sign-in method that provides an email.",
        )

    token = mint_deletion_token(uid)
    confirm_url = build_confirmation_url(token)
    send_deletion_email(email, confirm_url)
    return Response(status_code=204)


@router.post("/users/me/delete-account/confirm", status_code=204)
def confirm_account_deletion(
    body: ConfirmBody,
    user: dict = Depends(verify_bearer)
) -> Response:

    token_uid = consume_deletion_token(body.token.strip())
    auth_uid = user.get("uid")

    if token_uid != auth_uid:
        raise HTTPException(
            403,
            detail="Deletion token does not match authenticated user."
        )

    try:
        fb_auth.delete_user(auth_uid)
    except fb_auth.UserNotFoundError:
        pass

    return Response(status_code=204)