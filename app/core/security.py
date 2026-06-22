# app/core/security.py
"""
Security middleware for request validation, size limits, and safety headers.
"""
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException

logger = logging.getLogger(__name__)

MAX_REQUEST_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_GEOJSON_SIZE = 1 * 1024 * 1024  # 1 MB for GeoJSON specifically


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Prevent memory exhaustion from large payloads."""
    
    async def dispatch(self, request, call_next):
        if request.method in ["POST", "PUT", "PATCH"]:
            if "content-length" in request.headers:
                try:
                    content_length = int(request.headers["content-length"])
                    if content_length > MAX_REQUEST_SIZE:
                        logger.warning(
                            f"Request size violation: {content_length} bytes from {request.client.host}",
                            extra={"ip": request.client.host, "size": content_length}
                        )
                        return JSONResponse(
                            status_code=413,
                            content={"detail": "Request body too large"}
                        )
                except (ValueError, TypeError):
                    pass
        
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Enable HSTS
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # Content Security Policy - Restrict to same origin
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        # Prevent referrer leakage
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response


class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """Log errors and security events."""
    
    async def dispatch(self, request, call_next):
        try:
            response = await call_next(request)
            
            # Log suspicious requests
            if response.status_code >= 400:
                client_ip = request.client.host if request.client else "unknown"
                logger.warning(
                    f"API Error: {response.status_code} {request.method} {request.url.path}",
                    extra={
                        "ip": client_ip,
                        "status": response.status_code,
                        "path": request.url.path,
                        "method": request.method
                    }
                )
            
            return response
        except Exception as e:
            client_ip = request.client.host if request.client else "unknown"
            logger.error(
                f"Unhandled exception: {str(e)}",
                exc_info=True,
                extra={
                    "ip": client_ip,
                    "path": request.url.path,
                    "method": request.method
                }
            )
            # Return generic error to client
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )
