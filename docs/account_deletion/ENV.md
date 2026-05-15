# Account deletion — environment variables

These are read by **`app/services/account_deletion.py`**. Firebase Admin is initialized separately via **`app/core/firebase.py`** (service account at `secrets/firebase-admin.json` relative to the backend project root).

| Variable | Required | Purpose |
|----------|----------|---------|
| `ACCOUNT_DELETE_TOKEN_SECRET` | Yes (32+ chars) | HMAC secret for signed `delete_token` in email links. |
| `PUBLIC_APP_URL` | No (default `http://localhost:5173`) | SPA origin used in confirmation email (`?delete_token=…`). |
| `SMTP_HOST` | For email to send | Outgoing mail server. |
| `SMTP_PORT` | No (default `587`) | SMTP port. |
| `SMTP_USER` / `SMTP_PASSWORD` | If server requires auth | SMTP credentials. |
| `SMTP_FROM` | Yes for email | From address. |

If `ACCOUNT_DELETE_TOKEN_SECRET` is missing or too short, `POST .../request` returns **503** with a clear `detail` message so the rest of the API can still start.

If SMTP is not configured, the request endpoint returns **503** until mail is configured.
