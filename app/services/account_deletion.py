"""
Account deletion helpers (JWT link + SMTP).
Firebase Admin app initialized (app.core.firebase).
"""
from __future__ import annotations

import os
import smtplib
import urllib.parse
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText

import jwt
from fastapi import HTTPException


def _public_app_url() -> str:
    return (os.getenv("PUBLIC_APP_URL") or "http://localhost:5173").rstrip("/")


def _token_secret() -> str:
    s = (os.getenv("ACCOUNT_DELETE_TOKEN_SECRET") or "").strip()
    if len(s) < 32:
        raise HTTPException(
            503,
            detail="Account deletion is not configured (set ACCOUNT_DELETE_TOKEN_SECRET to a random string of at least 32 characters).",
        )
    return s


def mint_deletion_token(uid: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(hours=48)
    return jwt.encode(
        {"uid": uid, "typ": "acct_del", "exp": exp},
        _token_secret(),
        algorithm="HS256",
    )


def consume_deletion_token(token: str) -> str:
    try:
        data = jwt.decode(
            token,
            _token_secret(),
            algorithms=["HS256"],
            options={"require": ["exp"]},
        )
    except jwt.PyJWTError:
        raise HTTPException(400, detail="Invalid or expired confirmation link.")
    if data.get("typ") != "acct_del" or not data.get("uid"):
        raise HTTPException(400, detail="Invalid confirmation link.")
    return str(data["uid"])


def send_deletion_email(to_addr: str, confirm_url: str) -> None:
    smtp_host = os.getenv("SMTP_HOST", "").strip()
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "").strip()
    smtp_password = os.getenv("SMTP_PASSWORD", "").strip()
    smtp_from = os.getenv("SMTP_FROM", "").strip()

    if not smtp_host or not smtp_from:
        raise HTTPException(
            503,
            detail="Email is not configured on the server (set SMTP_HOST and SMTP_FROM).",
        )

    subject = "Confirm deletion of your SmartSeed account"
    body = f"""Hello,

You requested to permanently delete your SmartSeed Recommender account.

To complete deletion, open this link within 48 hours:

{confirm_url}

After you open the link, your Firebase account is removed and you will need a new account to sign in to SmartSeed again.

If you did NOT request this, ignore this email - your account will stay active.

- SmartSeed Recommender
"""

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = smtp_from
    msg["To"] = to_addr

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as smtp_conn:
            smtp_conn.starttls()
            if smtp_user:
                smtp_conn.login(smtp_user, smtp_password)
            smtp_conn.sendmail(smtp_from, [to_addr], msg.as_string())
    except OSError as e:
        raise HTTPException(503, detail=f"Could not send email: {e}") from e


def build_confirmation_url(token: str) -> str:
    q = urllib.parse.urlencode({"delete_token": token})
    return f"{_public_app_url()}/?{q}"
