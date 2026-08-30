# SWGOH Tracker v0.6

Functional v0.6 working build based on the current repository structure.

## Changes
- Ally Code save + Sync Now wired to backend.
- Public SWGOH.GG profile sync boundary; no private credentials.
- Local roster cache and sync history.
- GL/Solo journey screens consume synced roster data.
- Dashboard bottom navigation is hidden while on Dashboard.
- News is a continuously scrolling ticker.
- Upcoming Features renders `data/upcoming-features.json`.
- Version History uses icon-led bullet points.
- Existing dashboard, Conquest, GAC, Events, Resources and Team foundations retained.

## Backend
The backend is deliberately isolated in `backend/main.py`. It fetches the public SWGOH.GG player profile and normalises the returned data.

Deploy the backend to an HTTPS host, then set `API_BASE` in `config.js` to the backend URL plus `/api` if your host routes it that way.

This v0.6 build does NOT claim to synchronise private inventory. That remains provider-dependent.


## v0.6 scope

v0.6 is the feature release built on the v0.5 foundation.

Included/planned in this foundation:
- Roster-aware GAC counter architecture using AhnaldT101 as the team/meta source.
- Basic GAC planning and opponent-analysis foundations.
- Roster analysis.
- Advanced Conquest planning foundations that do not require private inventory.
- A future inventory-provider boundary for Lyutils.

Inventory-dependent calculations remain disabled until an approved Lyutils API/integration is available. The app must not request, capture, or reuse Lyutils passwords, session cookies, auth IDs, or one-time verification codes.

The v0.6.x series will be used for fixes and incremental improvements.
