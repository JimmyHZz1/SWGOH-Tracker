# v0.5 Sync Backend

This backend is the architecture change that fixes the v0.4 browser-to-third-party API problem. The PWA sends an Ally Code to this server; the server talks to a self-hosted SWGOH Comlink `/player` endpoint and returns only normalized profile/roster data to the PWA.

## Run

1. Install Python 3.10+.
2. Install dependencies: `pip install -r requirements.txt`
3. Run your self-hosted Comlink service.
4. Set `COMLINK_URL` if Comlink is not on `http://localhost:3000`.
5. Start: `uvicorn main:app --host 0.0.0.0 --port 8000`
6. In the PWA, set `config.js` `API_BASE` to the public URL of this backend, e.g. `https://tracker.example/api`.

The current backend intentionally does not handle EA credentials or private inventory. Those are reserved for the v0.6 investigation.
