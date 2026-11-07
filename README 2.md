# SWGOH Tracker v0.6

v0.6 introduces the Render-hosted Python backend foundation for roster synchronisation. This is a major backend/system change; it is not yet a completed or validated roster-sync release.

## What changed
- Added a separately hosted FastAPI backend deployed on Render.
- Added Render Blueprint configuration, Frankfurt region deployment and health-check routing.
- Added API health endpoints and aligned both `/sync` and `/api/sync` routes.
- Added CORS configuration for the GitHub Pages frontend.
- Kept the backend stateless; the PWA continues to retain its local roster cache.
- Improved API error handling so failures return readable JSON rather than raw upstream HTML or backend tracebacks.
- Updated the application and backend version identifiers to v0.6.

## Deployment status
- Render service: deployed at https://swgoh-tracker-api.onrender.com
- Health check: verified at `/api/health`, returning `ok: true` and version `0.5.1` at the time of the initial deployment.
- The v0.6 version update is being prepared on the `render-backend-fix` branch and requires a subsequent Render redeploy before the live service reports v0.6.

## Current blocker
A real Ally Code sync currently receives HTTP 403 from SWGOH.GG when the backend requests the character-roster page. The user's normal SWGOH.GG profile page loads in a browser, so automated access is being refused separately. An SWGOH.GG API application request has been submitted and is awaiting a decision. Do not claim roster or GP sync is working until a successful live test confirms it.

If API access is approved, credentials must be stored as Render environment variables/secrets, never committed to the repository or embedded in the PWA.

## Scope and limitations
- Current integration attempt uses public SWGOH.GG profile and roster pages.
- Public profile data does not provide private inventory, unequipped materials or crystal balances.
- Multi-user Ally Code support and end-to-end PWA sync must be validated after the upstream access issue is resolved.

## Deployment and release safety
- Render is configured from the `render-backend-fix` branch.
- The GitHub `main` branch and live GitHub Pages app have not been changed.
- Do not merge or publish without explicit approval.
- The planned v0.6 feature roadmap (including expanded GAC and Conquest tools) should be scheduled separately from completing and validating the backend foundation.
