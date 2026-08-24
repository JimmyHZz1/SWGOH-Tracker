# SWGOH Tracker PWA v0.5

Corrected feature-complete v0.5 build.

## Included
- Persistent title/version/GP/crystals header
- Rolling What's New banner
- Dashboard Journey Progress and Conquest widgets
- Square navigation tiles
- GL and Solo Journey sections
- Completed journeys moved to bottom by default
- Progress sorting and multiple manual pins
- My Priorities with manual overrides
- Conquest Planner, ticket tracking and static threshold fallback
- GAC counter catalogue foundation
- Events/watchlist foundation
- Resources/manual tracking foundation
- Team Builder
- Global Search
- Progress/sync history
- Version History (v0.2, v0.4, v0.5; no v0.3)
- Repository-editable Upcoming Features
- Multi-user-ready backend boundary
- Service-worker cache version bump to v0.5.1

## Sync
The PWA sends Ally Code requests to `config.js` -> `/api/sync`.
Deploy the backend in `backend/` and point `API_BASE` at its public HTTPS URL.

Private inventory authentication is intentionally reserved for v0.6.
