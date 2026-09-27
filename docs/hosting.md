# Put PatientPal online with Render

This guide is written for someone setting up a website for the first time. Follow the steps in order. You will put the app on GitHub, ask Render to run it, then open the web address Render gives you.

> **Before you start:** The old Gemini key was exposed in the repository. Revoke it and create a new one before publishing. This is a demo; do not upload real patient records.

> **Already created the Render Web Service?** This project now uses FastAPI with Uvicorn. In that service, open **Settings**, find **Build & Deploy**, and change **Start Command** to `uvicorn app:app --host 0.0.0.0 --port $PORT`. Save the change, then deploy the latest commit. Otherwise, Render will keep trying the old Gunicorn command.

> **The API files now live in `backend/`.** In the existing Web Service settings, change **Root Directory** from blank to `backend`. Keep the build command `pip install -r requirements.txt` and the Uvicorn start command above.

> **Already created the Static Site?** Its folder has been renamed to `frontend`. Open that Static Site's **Settings → Build & Deploy**, change **Root Directory** to `frontend`, and save so Render builds from the renamed folder.

## What you need

- A GitHub account with access to `CobaltConcrete/REPatientPal`.
- A Render account.
- A new Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
- The project saved on your computer, with its latest changes uploaded to GitHub.

## 1. Upload the app files to GitHub

Render gets the app from GitHub. If you use GitHub Desktop:

1. Open GitHub Desktop and select the `REPatientPal` project.
2. Look through the list of changed files. Do not commit `.env`; it holds private settings for your computer.
3. In the **Summary** box at the lower left, type `Prepare PatientPal for Render`.
4. Click **Commit to main**.
5. Click **Push origin** near the top. This uploads your changes to GitHub. Render can only build files that have been pushed.

If the latest project is already on GitHub, you can skip this step.

## 2. Start creating the website on Render

1. Go to [dashboard.render.com](https://dashboard.render.com/) and sign in.
2. Click **New +** (or **New**) and select **Web Service**.
3. If Render asks where your code is, choose **GitHub** and sign in to GitHub.
4. If GitHub asks which repositories Render can access, choose **Only select repositories**, select `CobaltConcrete/REPatientPal`, then click **Save** or **Install & Authorize**. This gives Render access to that private repository. If you see an **All repositories** option instead, you can choose it, but that gives Render access to all your repositories.
5. Return to Render. Find `CobaltConcrete/REPatientPal` in the repository list and click **Connect**. If it is missing, refresh the list. If it is still missing, open GitHub **Settings**, then **Applications**, then **Installed GitHub Apps**, choose **Render**, click **Configure**, and add `CobaltConcrete/REPatientPal` to the repository access list.

Choose **Web Service** for the Python API. You will make the separate public-facing website in Step 7.

## 3. Fill in the setup form

Enter these values. If a field listed here does not appear, leave it alone and continue.

| On the form | Enter or choose | In plain language |
|---|---|---|
| **Name** | `patientpal` | The name of the service. If Render says it is taken, try `patientpal-` followed by a few numbers. |
| **Region** | The nearest region available | Where Render runs the app. |
| **Branch** | `main` | The GitHub version Render should use. |
| **Language / Runtime** | **Python 3** | This is a Python service; do not choose Docker. |
| **Root Directory** | `backend` | This folder contains `app.py` and `requirements.txt`. |
| **Build Command** | `pip install -r requirements.txt` | Installs the parts the app needs to run, including FastAPI and Uvicorn. Copy exactly. |
| **Start Command** | `uvicorn app:app --host 0.0.0.0 --port $PORT` | Starts the API. Copy the whole line exactly. |
| **Instance Type** or **Plan** | **Free** | Enough for a personal demo. It may take a short time to start after being idle. |

For the backend Web Service, leave **Dockerfile Path** empty. This project does not use Docker; Render installs Python packages from `backend/requirements.txt`.

If these other fields appear, leave them empty:

- **Pre-Deploy Command**: leave blank. There is no database to prepare.
- **Publish Directory**: leave blank. This is for a different kind of website.

The Web Service runs the FastAPI API. The separate `frontend` folder contains the React website; you will publish it as a Static Site in Step 7.

## 4. Add the new Gemini key

On the setup form, find **Environment Variables**. These are private settings that Render gives to the app when it runs. Add each row using **Add Environment Variable** or the equivalent button:

| Name / Key | Value |
|---|---|
| `GEMINI_API_KEY` | Paste your **new** key from [Google AI Studio](https://aistudio.google.com/app/apikey). If there is a **Secret** switch, turn it on. |
| `GEMINI_MODEL` | `gemini-3.8-flash` |
| `MAX_UPLOAD_MB` | `8` |
| `LOG_LEVEL` | `INFO` *(optional)* |

Keep the key in Render's environment settings. Do not put it in GitHub, this guide, your source code, or `render.yaml`. On your own computer, the key belongs in `backend/.env`, written like `GEMINI_API_KEY=paste-your-new-key-here`.

## 5. Create and open the API service

1. Review the settings and make sure the new Gemini key is entered.
2. Click **Create Web Service** or **Deploy Web Service**.
3. Render will show a page with activity and logs while it sets up the app. Wait until it says the service is live. The first setup can take several minutes.
4. Click the web address ending in `onrender.com` near the top of the page. This is the API address. Copy it somewhere; you will need it for the frontend.

Render explains [Web Service setup](https://render.com/docs/your-first-deploy). FastAPI's official guide explains [running the app with Uvicorn](https://fastapi.tiangolo.com/deployment/manually/).

## 6. Check the API service

1. Open the API address followed by `/health`, for example `https://patientpal.onrender.com/health`. You should see `{"status":"ok"}`. Your address may have a different name.
2. If it does not work, open **Logs** on the Render service page. Check that the key is entered correctly and that the latest app files were pushed to GitHub.

### If the log still says `gunicorn: command not found`

The pip update notice is harmless. This app now uses Uvicorn, so Render must use the new start command. Open the Web Service's **Settings**, find **Build & Deploy**, edit **Start Command** to `uvicorn app:app --host 0.0.0.0 --port $PORT`, and save. Confirm **Build Command** is `pip install -r requirements.txt`, then choose **Manual Deploy → Deploy latest commit**. The latest GitHub version must include the updated `requirements.txt`.

## 7. Create the public website as a Static Site

The Static Site is the page your visitors will open. It sends image uploads to the Web Service API from Step 5. Both services use the same GitHub repository, but different folders and settings.

1. In the Render dashboard, click **New +** and choose **Static Site**.
2. Select the same GitHub repository, `CobaltConcrete/REPatientPal`. If it is not listed, ask the repository owner or administrator to grant Render access to it.
3. Choose branch **`main`**, then fill in the form:

| On the form | Enter this | Why |
|---|---|---|
| **Name** | `patientpal-frontend` (or another available name) | This becomes part of the website address. |
| **Root Directory** | `frontend` | The React website files are in this folder. |
| **Build Command** | `npm ci && npm run build` | Installs the website packages and prepares the finished website. |
| **Publish Directory** | `build` | This is the folder made by the build command. |

4. Find **Environment Variables** and add this row. Use the API address copied in Step 5, with `/upload` at the end:

   | Key | Value |
   |---|---|
   | `REACT_APP_API_URL` | `https://your-api-name.onrender.com/upload` |

   Replace `your-api-name` with the real Web Service address. Do not add the Gemini key to the Static Site; the key belongs only on the private API service.

5. Choose the **Free** plan if Render offers it, then click **Create Static Site**.
6. Wait for the site to say it is live. Copy its address ending in `onrender.com`; this is the address you give to users.

## 8. Connect the website to the API

The API only accepts browser requests from the website address you allow. Add that address to the API service:

1. Open the **Web Service** in Render and click **Environment**.
2. Click **Add Environment Variable**.
3. Set the key to `FRONTEND_ORIGIN` and the value to the full Static Site address, such as `https://patientpal-frontend.onrender.com`. Do not add a path or a final slash.
4. Click **Save, rebuild, and deploy** (or the equivalent save-and-deploy option).
5. When the API is live again, open the Static Site address and try a sample image with no real patient information.

If you later change the Static Site name or add a custom domain, update `FRONTEND_ORIGIN` on the API service to match the new address, then redeploy the API.

If the page loads but cannot reach the API, confirm that `REACT_APP_API_URL` on the Static Site is the API's `/upload` address, and that `FRONTEND_ORIGIN` on the Web Service exactly matches the Static Site address. Save and redeploy both after changing their settings.

## Do I need to set up a database?

No. This version does not have accounts or saved history. It handles an upload, returns the result, and does not save the image, text, translation, or audio. You do not need Postgres, Supabase, or another database to put this version online.

If you later add accounts or saved preferences, a database may be useful. Supabase Postgres is one option for ordinary account settings. Do not save identifiable medical documents in a free database or file bucket. Keeping health records requires careful privacy and security planning, including rules for who can access and delete them.

## What happens when someone uses the demo?

- The uploaded image is sent to **Google Gemini** to read, explain, and translate it.
- The translated text is sent to **gTTS** to make spoken audio.
- This app does not save the upload or the generated result.

Tell people what happens to their upload before they use the app. This demo is not for diagnosis or treatment decisions.

## What is running on Render?

There are two services. The **Static Site** shows the React website that visitors use. The **Web Service** receives uploads, asks Gemini to process them, and uses gTTS to create audio. FastAPI also provides interactive API docs at `/docs`. The Gemini key stays on the Web Service and is never put in the website. The API service settings are also recorded in [`render.yaml`](../render.yaml); you do not need to open that file for the steps above.

