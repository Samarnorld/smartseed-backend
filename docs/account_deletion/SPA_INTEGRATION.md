# Account deletion ↔ SmartSeed web app

Implementation in this repo:

- **`app/api/endpoints/account_deletion.py`** — HTTP routes (mounted under `/api` in `app/main.py`).
- **`app/services/account_deletion.py`** — JWT mint/verify, SMTP body, `PUBLIC_APP_URL`.

Firebase verification and user deletion use the same **`firebase_admin`** app as the rest of the backend (`app/core/firebase.py`).

The SPA runs with **`npm run dev`**; this backend runs with **`uvicorn app.main:app`** from the **`smartseed-backend/`** directory.

## Base URL (`VITE_API_URL`)

From the frontend `apiClient.ts`:

- `API_BASE_URL = import.meta.env.VITE_API_URL || "https://api.greencitiesmap.com/api"`
- Account paths: `/users/me/delete-account/request` and `/users/me/delete-account/confirm`.

Full URLs (local example): `http://127.0.0.1:8000/api/users/me/delete-account/request` when `VITE_API_URL=http://127.0.0.1:8000/api`.

## Endpoints

| SPA helper | Method | Path (after `API_BASE_URL`) | Auth |
|------------|--------|-----------------------------|------|
| `requestAccountDeletionEmail` | `POST` | `/users/me/delete-account/request` | Bearer Firebase ID token |
| `confirmAccountDeletionFromEmail` | `POST` | `/users/me/delete-account/confirm` | None |

### Confirm body

`Content-Type: application/json`, `{"token": "<string>"}`.

### Success

SPA accepts **200** or **204**.

### Error JSON (SPA parsing)

See `readErrorMessageFromResponse` in `src/utils/api.ts`: prefers `message`, then string `detail`, then FastAPI-style `detail` array with `msg`, else truncated plain text.

### Client timeout

`DELETE_ACCOUNT_TIMEOUT_MS` = **25000** in the SPA.

## Email link

`{PUBLIC_APP_URL}/?delete_token=<token>` — SPA also supports `#delete_token=…`.

## Related

- **`ENV.md`** — variables for this feature.
- **`STANDALONE.md`** — run this backend repo next to the SPA.
