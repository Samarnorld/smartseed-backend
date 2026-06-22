# app/core/limiter.py
from slowapi import Limiter
from fastapi import Request
import os

def get_safe_client_ip(request: Request) -> str:
    """
    Safely resolves the true client IP from standard proxy headers.
    Checks headers in order of trust/specificity.
    """
    # 1. Cloudflare
    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip:
        return cf_ip.strip()

    # 2. Forwarded list (first element is the original client IP)
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()

    # 3. Real IP header
    x_real_ip = request.headers.get("x-real-ip")
    if x_real_ip:
        return x_real_ip.strip()

    # 4. Fallback to direct client TCP host
    return request.client.host if request.client else "127.0.0.1"


def rate_limit_key(request: Request) -> str:
    """
    Generates a deterministic rate limit key.
    Uses the Authorization token if present to prevent IP rotation bypass.
    Falls back to a proxy-safe client IP address.
    """
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.removeprefix("Bearer ").strip()
        if token:
            # Rate limit by unique token (identity)
            return f"user:{token}"

    # Fall back to safe IP
    ip = get_safe_client_ip(request)
    return f"ip:{ip}"


# Storage configuration: defaults to in-memory, but supports Redis in production
# via env var (e.g. RATELIMIT_STORAGE_URI=redis://localhost:6379)
storage_uri = os.getenv("RATELIMIT_STORAGE_URI", "memory://")

limiter = Limiter(key_func=rate_limit_key, storage_uri=storage_uri)
