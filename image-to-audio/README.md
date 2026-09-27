# PatientPal website

This React website is deployed separately from the Python API. For the beginner-friendly Render steps, see [the hosting guide](../docs/hosting.md).

## Run on your computer

1. Start the Flask API at `http://127.0.0.1:5000` using the root README.
2. Open a terminal in this folder (`image-to-audio`).
3. Run `npm install` once, then run `npm start`.
4. The website opens at `http://localhost:3000`; the development server forwards API requests to the Flask app.

## Deploy as a Render Static Site

- **Root Directory:** `image-to-audio`
- **Build Command:** `npm ci && npm run build`
- **Publish Directory:** `build`
- **Environment variable:** `REACT_APP_API_URL=https://YOUR-API.onrender.com/upload`

Replace `YOUR-API` with the Web Service address. Set `FRONTEND_ORIGIN` on the Python Web Service to the Static Site's `https://YOUR-SITE.onrender.com` address. Never put the Gemini key in this website; it belongs only in the Web Service's environment variables.
