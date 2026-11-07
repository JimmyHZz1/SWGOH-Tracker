# SWGOH Tracker API — Render deployment

This repository uses the **root-level `main.py`** as the Render service entry point. It reads public SWGOH.GG profile and character pages; it does not provide private inventory access.

## Deploy on Render

1. In Render, choose **New → Blueprint** and connect `JimmyHZz1/SWGOH-Tracker`.
2. Select branch `render-backend-fix` for this test deployment.
3. Render detects `render.yaml`. Review the service named `swgoh-tracker-api` and create it.
4. Once deployed, open the service URL and check `https://YOUR-SERVICE.onrender.com/api/health`. It should return JSON with `"ok": true`.
5. Copy the service's HTTPS URL. In the PWA's `config.js`, set `API_BASE` to that URL followed by `/api`, for example:
   ```js
   window.SWGOH_CONFIG = {
     API_BASE: "https://swgoh-tracker-api.onrender.com/api"
   };
   ```
   This frontend configuration is deliberately not pointed at a live Render service until one exists.
6. When ready, publish the frontend config change through a separately reviewed update. This branch does not alter GitHub Pages or `main`.

## Render settings

- Root directory: repository root (leave blank).
- Build command: `pip install -r requirements.txt`.
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`.
- Health check: `/api/health`.
- `CORS_ORIGINS`: comma-separated allowed website origins, without paths. The default is `https://jimmyhzz1.github.io`; add your own custom domain here if you use one.

The API accepts `POST /api/sync` (also `POST /sync`) with JSON `{"allyCode":"123456789"}`. Health is available at `GET /api/health` (also `GET /health`).

## Important limitations

- Render's free service may sleep when idle; the first request after sleeping can take longer while it wakes.
- The service is stateless. The PWA should keep its own local cache of the last successful roster.
- SWGOH.GG may change its page markup or rate-limit automated requests. A successful HTTP response does not guarantee every roster field can be parsed; test against a real profile before relying on it.
- Only public profile/roster data is returned. Crystals and private inventory are not populated by this public-page method.
- Do not deploy the legacy `backend/` directory as the service root. It contains the previous implementation and is not the Render entry point for this branch.
