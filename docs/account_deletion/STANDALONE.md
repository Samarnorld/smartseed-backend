# Account deletion in the standalone `smartseed-backend` repo

1. Configure **`secrets/firebase-admin.json`** (already required for the main API — see `app/core/firebase.py`).
2. Add account-deletion env vars — see **`ENV.md`** in this folder (`ACCOUNT_DELETE_TOKEN_SECRET`, `PUBLIC_APP_URL`, `SMTP_*`).
3. From **`smartseed-backend/`** install deps and run:

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

4. In the **smartseed-recommender** (frontend) project, set:

```text
VITE_API_URL=http://127.0.0.1:8000/api
```

5. Keep using **`npm run dev`** for the frontend; do not replace it with uvicorn.

When you move **`smartseed-backend/`** out of the monorepo, take **`docs/account_deletion/`** with it so the SPA contract stays documented next to the code.
