# Set up PatientPal

This guide explains how to put the web version online with GitHub and Render. The project is split into three app folders:

- `backend/` — the FastAPI service that processes uploads.
- `frontend/` — the React website that people open in a browser.
- `mobile-app/` — an optional Expo mobile app prototype.

The web version uses two Render services: a **Web Service** for the backend and a **Static Site** for the frontend. Do not upload real patient records; this is a demo.

> **Key safety:** An older Gemini key was exposed in the repository. Revoke it and create a replacement before deploying. Keep the new key only in the backend's Render environment settings or in your ignored local `backend/.env` file.

## GitHub

Render downloads the code from GitHub, so the changes must be pushed before Render can use them.

If you use GitHub Desktop:

1. Open GitHub Desktop and choose the `REPatientPal` project.
2. Review the changed files. Do not commit `.env` files; they contain private settings. Files ending in `.env.example` are safe to commit because they contain placeholders.
3. Enter a short note in the **Summary** box, such as `Prepare PatientPal for Render`.
4. Click **Commit to main**, then **Push origin**.

If Render cannot find the private repository:

1. In Render, choose GitHub when connecting a repository.
2. On GitHub's access page, choose **Only select repositories**, select `CobaltConcrete/REPatientPal`, then choose **Save** or **Install & Authorize**.
3. If it is not listed, ask the repository owner or administrator to grant Render access. A non-owner may not have permission to change access to a private repository.

## Backend Web Service

The Web Service runs the Python API. If you already created it, update its settings as shown below before deploying the latest commit.

In Render, choose **New + → Web Service**, connect `CobaltConcrete/REPatientPal`, and enter:

| Setting | Enter this |
|---|---|
| **Name** | `patientpal` (or another available name) |
| **Branch** | `main` |
| **Language / Runtime** | **Python 3** |
| **Root Directory** | `backend` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python serve.py` |
| **Health Check Path** | `/health` |
| **Plan / Instance Type** | **Free** for a demo |
| **Dockerfile Path** | Leave empty; this service uses Python, not Docker. |

Leave **Pre-Deploy Command** and **Publish Directory** empty. The build and start commands run from `backend/`, so use the commands above without adding `backend/` to their paths.

If the Web Service already exists, open **Settings > Build & Deploy** and set **Root Directory** to `backend`. Set **Start Command** to `python serve.py`; the old service setting may still contain the Uvicorn command. Save the changes and deploy the latest commit.

Add these settings under **Environment → Environment Variables**:

| Key | Value |
|---|---|
| `GEMINI_API_KEY` | Your new key from [Google AI Studio](https://aistudio.google.com/app/apikey). Keep it secret. |
| `GEMINI_MODEL` | `gemini-3.8-flash` |
| `MAX_UPLOAD_MB` | `8` |
| `LOG_LEVEL` | `INFO` (optional) |

After the Static Site is created, add one more variable here: `FRONTEND_ORIGIN` = the full Static Site address, such as `https://patientpal-frontend.onrender.com`. Leave off any path and trailing slash. Save and redeploy the Web Service after setting it.

When Render says the service is live, open `https://YOUR-SERVICE.onrender.com/health`. The response should be `{"status":"ok"}`. The interactive API documentation is at `/docs`.

### If the log says the port is invalid or Uvicorn cannot start

The pip upgrade notice is informational. The log you shared shows an invisible character after `$PORT`, so Uvicorn receives `10000` plus that character and rejects the port. The `backend/serve.py` launcher reads Render's port setting inside Python, avoiding `$PORT` in the Render command.

1. Open the Web Service **Settings > Build & Deploy**.
2. Click **Edit** beside **Start Command**, clear the whole field, then type this command:

   `python serve.py`

3. Confirm **Root Directory** is `backend` and **Build Command** is `pip install -r requirements.txt`.
4. Save the changes, then choose **Manual Deploy > Deploy latest commit**.

The backend's `requirements.txt` includes Uvicorn. If it still cannot start, check that the build log installs the requirements from `backend/requirements.txt` successfully.

## Frontend Static Site

The Static Site publishes the React website for people to use. In Render, choose **New + → Static Site**, connect the same GitHub repository, then set:

| Setting | Enter this |
|---|---|
| **Name** | `patientpal-frontend` (or another available name) |
| **Branch** | `main` |
| **Root Directory** | `frontend` |
| **Build Command** | `npm ci && npm run build` |
| **Publish Directory** | `build` |

Under **Environment Variables**, add this row:

| Key | Value |
|---|---|
| `REACT_APP_API_URL` | `https://YOUR-SERVICE.onrender.com/upload` (replace `YOUR-SERVICE` with your Web Service name) |

Keep the Gemini key on the Backend Web Service. Never add it to the Static Site.

Create the Static Site and wait for it to say live. Its `onrender.com` address is the website address to share with users. Copy that exact address into `FRONTEND_ORIGIN` on the Backend Web Service, save, and redeploy the backend. If the website cannot reach the API, check that `REACT_APP_API_URL` ends in `/upload` and `FRONTEND_ORIGIN` exactly matches the Static Site address.

If you already created a Static Site before the folder was renamed, open **Settings → Build & Deploy** and change **Root Directory** to `frontend`.

## Mobile App

**Status: a prototype exists, but the mobile app is not ready to publish.** The code in `mobile-app/` has an Expo project and a basic screen that can select a photo, choose a language, send it to the API, and display the summary and translation. It does not play the generated audio. It has not been verified as a complete iOS or Android app, built for app stores, or published.

The Render Web Service can also receive requests from the mobile app, but the app needs the deployed API address in `mobile-app/.env`:

```text
EXPO_PUBLIC_API_URL=https://YOUR-SERVICE.onrender.com
```

This is only the API address; do not add `/upload` because the app adds that path itself. A working web deployment does not automatically publish the mobile app. Before distributing it, the Expo/native image-picker setup needs to be validated on real devices, audio behavior decided, and iOS/Android builds prepared.

## Storage and privacy

This version has no accounts or saved history, so it does not need a database. It processes an upload and returns results without saving the image, text, translation, or audio in its own storage. Do not add a database just to deploy this version.

The uploaded image is sent to Google Gemini to read and explain it. The translated text is sent to gTTS to create audio. Tell users about this processing before they upload anything. Do not use this demo for diagnoses, treatment decisions, or real patient records.

The backend's Render settings are also recorded in [`render.yaml`](../render.yaml). Render's [monorepo guide](https://render.com/docs/monorepo-support) explains how service root directories work; FastAPI's [Uvicorn guide](https://fastapi.tiangolo.com/deployment/manually/) explains the server command.
