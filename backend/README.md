# v0.5 Sync Backend

POST `/sync` with `{ "allyCode": "337627356" }`.

This backend is a secure boundary between the PWA and a self-hosted Comlink instance. Do not put Comlink/API secrets in the PWA.

Set `COMLINK_URL` to your Comlink service. Add authentication in the deployment environment if your Comlink instance is protected.
