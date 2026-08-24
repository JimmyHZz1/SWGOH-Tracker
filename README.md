# SWGOH Tracker v0.5

Major feature-frozen build based on the supplied v0.4 project, with the v0.2 project retained as the historical baseline.

## Included
- Redesigned dashboard with persistent GP/Crystals header and v0.5 label
- Rolling What's New banner
- Journey Progress widget
- Conquest widget with progress, tickets and manual fallback/countdown placeholder
- Square navigation tiles
- GL/Solo Journey/Characters/Resources/GAC/Events/Teams sections
- Multi-user-ready Ally Code sync architecture
- Local cache, export/reset and last-sync state
- Version History for v0.2, v0.4 and v0.5 (v0.3 omitted because it was never built)
- Repository-editable Upcoming Features JSON
- Backend proxy for self-hosted SWGOH Comlink
- v0.6 placeholder for authorised private-inventory integration

## Important
The frontend no longer calls SWGOH data services directly. To make Ally Code sync live over the internet, deploy the backend and a self-hosted Comlink instance, then set `config.js` `API_BASE` to the backend URL. Do not put private Comlink/HMAC secrets in the PWA.

The v0.5 resource page deliberately does not claim access to private inventory. That work is planned for v0.6.
