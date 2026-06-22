# DEPLOYMENT & TESTING GUIDE

## Quick Start for Production

### 1. Rotate All Secrets NOW ⚠️

```bash
# Generate new account deletion token
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Output: XYZ...abc (use this in ACCOUNT_DELETE_TOKEN_SECRET)

# For Gmail SMTP - Get app password:
# 1. Go to https://myaccount.google.com/apppasswords
# 2. Select Mail & Windows/Linux
# 3. Copy generated app password
# 4. Use as SMTP_PASSWORD
```

### 2. Update .env File

```bash
# Edit .env and replace:
ACCOUNT_DELETE_TOKEN_SECRET=<new-secure-token-from-above>
SMTP_PASSWORD=<gmail-app-password>
REDIS_PASSWORD=<strong-random-password>

# Example secure password generation:
python -c "import secrets; print(secrets.token_urlsafe(24))"
```

### 3. Configure for Your Domain

```bash
# Update ALLOWED_ORIGINS to your domain(s)
ALLOWED_ORIGINS=https://smartaseed.cliffordgeoconsult.com,https://app.smartaseed.com

# Update SMTP sender
SMTP_USER=your-email@yourdomain.com
SMTP_FROM=noreply@yourdomain.com
PUBLIC_APP_URL=https://smartaseed.cliffordgeoconsult.com
```

### 4. Configure Redis for Production

```bash
# If using remote Redis:
REDIS_HOST=redis.example.com
REDIS_PORT=6379
REDIS_PASSWORD=<your-strong-password>
REDIS_SSL=true
REDIS_CERT_FILE=/path/to/redis-ca.pem

# For distributed rate limiting across multiple instances:
RATELIMIT_STORAGE_URI=redis://:your-password@redis.example.com:6379/0
```

---

## Verify Security Fixes

### Test 1: Rate Limiting Works

```bash
# Get a valid Firebase token from your frontend
export TOKEN="your_valid_firebase_token"

# Call an endpoint 21 times (limit is 20/minute)
for i in {1..21}; do
  echo "Request $i:"
  curl -s -H "Authorization: Bearer $TOKEN" \
    https://api.example.com/api/rainfall/annual \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"geometry":{"type":"Point","coordinates":[35.0,-0.5]},"year":2023}' \
    | grep -o "status_code.*"
  sleep 0.5
done

# Expected: Requests 1-20 succeed, request 21 returns 429 Too Many Requests
```

### Test 2: Authentication Required

```bash
# Without token - should fail
curl -X POST https://api.example.com/api/rainfall/annual
# Expected: 403 Forbidden or 401 Unauthorized

# With invalid token - should fail
curl -H "Authorization: Bearer invalid-token" \
  -X POST https://api.example.com/api/rainfall/annual
# Expected: 401 Unauthorized
```

### Test 3: CORS Restrictions Work

```bash
# From different origin - should be blocked
curl -H "Origin: https://attacker.com" \
  -H "Access-Control-Request-Method: POST" \
  -X OPTIONS https://api.example.com/api/rainfall/annual

# Check response headers - should NOT have Access-Control-Allow-Origin
```

### Test 4: Input Validation

```bash
# Invalid coordinates (lat > 90)
curl -H "Authorization: Bearer $TOKEN" \
  "https://api.example.com/api/ward-from-point?lat=200&lon=0"
# Expected: 422 Unprocessable Entity

# Invalid date range (end before start)
curl -H "Authorization: Bearer $TOKEN" \
  -X POST -H "Content-Type: application/json" \
  -d '{"geometry":{"type":"Point","coordinates":[35.0,-0.5]},"start_date":"2024-12-31","end_date":"2024-01-01"}' \
  https://api.example.com/api/rainfall/analyze
# Expected: 422 Unprocessable Entity
```

### Test 5: Error Messages Don't Leak Details

```bash
# Send invalid geometry
curl -H "Authorization: Bearer $TOKEN" \
  -X POST https://api.example.com/api/rainfall/analyze \
  -H "Content-Type: application/json" \
  -d '{"geometry":"invalid","start_date":"2024-01-01","end_date":"2024-12-31"}'

# Response should be generic: {"detail":"Invalid geometry provided"}
# NOT: {"detail":"'coordinates' key required in GeoJSON..."}
```

---

## Remaining Endpoints to Secure

The following endpoints were not yet updated in this batch (apply same pattern):

1. **Tile Endpoints:** (lower priority, compute-heavy)
   - `/ndvi/tiles`
   - `/rainfall/tiles`
   - `/elevation_tiles`
   - `/soil/tiles`
   - `/temperature/tiles`

2. **Monthly/Anomaly Endpoints:**
   - `/rainfall/monthly`
   - `/temperature/monthly`
   - `/temperature/anomaly`

3. **Other Data Endpoints:**
   - `/nandi/seed` (if exists)

### How to Update Remaining Endpoints

```python
# Pattern to follow for each remaining endpoint:

import logging
from fastapi import APIRouter, Request, Depends, HTTPException
from app.core.limiter import limiter
from app.api.deps import get_current_user
from app.services.gee.geometry import geojson_to_ee

logger = logging.getLogger(__name__)

@router.post("/endpoint-name")
@limiter.limit("20/minute")  # Add rate limit
def endpoint_handler(
    request: Request,
    geometry: dict,  # Accept dict, not ee.Geometry
    user: dict = Depends(get_current_user),  # Add authentication
):
    """Description of endpoint."""
    try:
        ee_geometry = geojson_to_ee(geometry)
        logger.info(f"Endpoint called by {user.get('uid')}")
        # ... rest of logic
    except Exception as e:
        logger.error(f"Endpoint failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis failed")
```

---

## Docker Deployment Example

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/gee/health')"

# Run with gunicorn for production
CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

```bash
# Build and run
docker build -t smartseed-api .
docker run -p 8000:8000 \
  --env-file .env.production \
  -e REDIS_HOST=redis \
  smartseed-api
```

---

## Monitoring & Alerts

### Logs to Watch For:

```bash
# Check for failed authentications
docker logs smartseed-api | grep "Authentication failed"

# Check for rate limit violations
docker logs smartseed-api | grep "request size violation"

# Check for errors
docker logs smartseed-api | grep "ERROR"
```

### Example Monitoring Query (Cloud Logging):

```
resource.type="cloud_run"
resource.labels.service_name="smartseed-api"
severity >= ERROR
OR
jsonPayload.message =~ "Authentication failed"
OR
jsonPayload.message =~ "rate limit"
```

---

## Dependency Updates

Before deploying to production:

```bash
# Check for security vulnerabilities
pip install safety
safety check --file requirements.txt

# OR use pip-audit
pip install pip-audit
pip-audit --requirement requirements.txt

# Fix critical vulnerabilities
pip install --upgrade <package-name>
```

---

## Post-Deployment Verification

After deploying to production:

1. **Check Status:**
   ```bash
   curl https://api.example.com/  # Should return welcome message
   curl https://api.example.com/gee/health  # Should show GEE status
   ```

2. **Verify CORS Headers:**
   ```bash
   curl -I https://api.example.com/  
   # Should show Strict-Transport-Security, X-Frame-Options, etc.
   ```

3. **Test All Security Headers:**
   ```bash
   https://observatory.mozilla.org/
   # Enter your API domain, should score A+ or A
   ```

4. **Run Security Scan:**
   ```bash
   nmap -p 8000 api.example.com
   nmap --script ssl-enum-ciphers -p 443 api.example.com
   ```

---

## Rollback Plan

If security issues occur:

```bash
# Quick rollback to previous version
docker pull smartseed-api:previous-tag
docker stop smartseed-api
docker run -p 8000:8000 --env-file .env.production smartseed-api:previous-tag

# Investigate logs
docker logs smartseed-api-old > /tmp/crash.log
# Review security issues in crash.log
```

---

## Support Resources

- **FastAPI Security**: https://fastapi.tiangolo.com/tutorial/security/
- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **Firebase Auth**: https://firebase.google.com/docs/auth
- **Rate Limiting Best Practices**: https://tools.ietf.org/html/draft-polli-ratelimit-headers
- **Security Headers**: https://securityheaders.com

---

**Status**: Phase 1 Security Hardening Complete ✅  
**Next**: Deploy, Monitor, Phase 2 - Advanced Hardening  
**Support**: Review SECURITY_FIXES.md for detailed information
