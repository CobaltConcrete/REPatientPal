# PatientPal

PatientPal is a small web prototype that reads a photo of a medical document, creates a plain-language summary, translates it, and generates speech. It is a language-accessibility demo, not a diagnostic or clinical tool.

## Run locally

Use Python 3.12. Create and activate a virtual environment, install dependencies, and make a local environment file (skip the copy step if `.env` already exists):

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Open `.env` and set `GEMINI_API_KEY` to a new key from [Google AI Studio](https://aistudio.google.com/app/apikey). Start the API:

```powershell
uvicorn app:app --reload
```

Open <http://127.0.0.1:8000/docs> for interactive API documentation. The endpoint accepts multipart form data at `POST /upload` with `file` and `language` fields (`english`, `chinese`, `cantonese`, or `hindi`). `GET /health` is the deployment health check.

## Environment variables

| Variable | Required | Purpose |
|---|---:|---|
| `GEMINI_API_KEY` | Yes | Server-side Gemini API credential. Never put it in browser code or commit `.env`. |
| `GEMINI_MODEL` | No | Gemini model ID; defaults to `gemini-3.8-flash`. |
| `MAX_UPLOAD_MB` | No | Upload limit; defaults to 8 MB. |
| `LOG_LEVEL` | No | Python log level; defaults to `INFO`. |
| `FRONTEND_ORIGIN` | No | Comma-separated website origins allowed to call the API from a browser. Set this to the Render Static Site URL. |

The same Gemini credential is used for image understanding, summarization, and translation. gTTS creates speech without a key. There is no speech-to-text feature or translation-provider key in this version.

The optional Expo mobile app in `PatientPal/` reads `EXPO_PUBLIC_API_URL` from `PatientPal/.env`; copy its example file and set the deployed server URL. It returns text results only. The Create React App website in `frontend/` can be deployed as a Render Static Site; set `REACT_APP_API_URL` to the deployed API endpoint ending in `/upload`. The API must allow the Static Site's address through `FRONTEND_ORIGIN`.

## Privacy and storage

This app does not save uploaded images, reports, translations, or generated audio to its own filesystem or a database. The image is sent to Google Gemini for processing; translated text is sent to gTTS to create audio. Configure those providers and obtain appropriate consent before using real health documents. Do not use this prototype for clinical decisions or store identifiable health information without a security, privacy, and regulatory review.

## Deployment

See [docs/hosting.md](docs/hosting.md) for the Render setup, secret configuration, storage decision, and deployment checklist. `render.yaml` is a deploy blueprint; it intentionally has no database because the current product has no account/history feature.
