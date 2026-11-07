# SWGOH Tracker v0.5.1

v0.5.1 is a maintenance and backend-fix release. It does not introduce the planned v0.6 feature set.

## Fixes and improvements
- Prepared a dedicated Python backend for deployment on Render.
- Added a Render Blueprint configuration and deployment instructions.
- Added health-check endpoints for deployment diagnostics.
- Aligned the API to accept both `/sync` and `/api/sync` routes.
- Improved public SWGOH.GG profile and roster sync error handling.
- Configured CORS for the GitHub Pages frontend.
- Ensured sync failures return readable JSON messages rather than raw HTML or backend tracebacks.
- Documented the legacy backend to reduce the risk of deploying the wrong implementation.
- Kept the backend stateless; the PWA retains its local roster cache.

## Scope and limitations
- Sync uses public SWGOH.GG profile and roster pages.
- Private inventory, unequipped materials and crystal balances are not provided by this public sync.
- The Render service has been prepared, but a live deployment and real-profile parser validation are still required.

## Deployment
Deploy the `render-backend-fix` branch to Render using `render.yaml`. After Render creates the service, set the service URL in `config.js` and test `/api/health` before attempting an Ally Code sync.

The main branch and live GitHub Pages app are not changed by this maintenance branch.

## Future release
The planned v0.6 feature work remains separate from this maintenance release.
