# Local secrets (frontend repo root)

Place **real credential files here only on your machine**. Do **not** commit private keys or service account JSON to git.

## Expected files

| File | Used by | How to obtain |
|------|---------|----------------|
| **`firebase-admin.json`** | Python backend (Firebase Admin SDK) when `FIREBASE_CREDENTIALS_PATH` points here | Firebase Console → Project settings → Service accounts → Generate new private key. Save as `firebase-admin.json` in this folder. |

From the nested **`server/`** app, a typical `.env` entry is:

```env
FIREBASE_CREDENTIALS_PATH=../secrets/firebase-admin.json
```

If your main API lives in **`smartseed-backend/`**, it often expects `smartseed-backend/secrets/firebase-admin.json` — you can **copy** the same file into that path, or keep one canonical copy and point env vars to it.

## Safe template

`firebase-admin.json.example` in this folder shows the JSON **shape** only. Copy it to `firebase-admin.json` and replace every value with the real key from Firebase (never commit `firebase-admin.json`).
