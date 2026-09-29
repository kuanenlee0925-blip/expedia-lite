# Assignment 2 — hotel search, map, and persistent shortlist

Published report draft, September 29, 2026. This is separate from the older
sample-booking Part 2 report at the project root.

## Project access and startup

Existing repository: https://github.com/kuanenlee0925-blip/expedia-lite

**Assignment 2 application checkpoint:** [2a979ce81aa70b45c50f962c47b0ba2a27c0ee0e](https://github.com/kuanenlee0925-blip/expedia-lite/commit/2a979ce81aa70b45c50f962c47b0ba2a27c0ee0e). Published to main at the student's request; final student review remains pending.
The earlier booking checkpoint does not include this work. Follow
[README setup and configuration](../README.md). Open http://127.0.0.1:5173
with FastAPI on port 8000. The project-root `.env` is backend-only; restart
the backend after changing it. Never include its contents in evidence.
The health endpoint reports configuration status without revealing the key.

## Research, design, and implementation

[Research and early mockup](assignment2-research-and-design.md) covers both
the hotel list/map and shortlist additions. The saved shortlist appears below
the search so it remains available when live results change. The implemented
list scrolls to keep a long provider response from overwhelming the map.

Vue Views: `frontend/src/NearbyHotels.vue` and `HotelMap.vue`.
FastAPI routes: `backend/main.py`. Controllers: `backend/zip_lookup.py`,
`places.py`, and `shortlist.py`. Configuration: `backend/config.py`.
External place snapshots and SQLite tables form the data model independently
of sample hotels that require a price. AGENTS.md records these responsibilities.

A submitted ZIP flows from Vue to `/api/hotels`, through postcode verification
and Geoapify Places, back to normalized results and synchronized Leaflet markers.
The radius is 5 km around the provider's verified postcode point, not the user's
location. At most 20 results are requested; no exhaustive coverage is claimed.
Snapshots are saved locally by provider place ID and remain after backend restart.

## Demonstration and verification

[Watch the student's Assignment 2 demonstration (MP4, approximately 55 seconds)](https://github.com/kuanenlee0925-blip/expedia-lite/raw/refs/heads/main/media/assignment2-part1-demonstration.mp4).
Recorded September 29, 2026. Shows live searches for 16802 and 33647, loading,
hotel lists/maps, shortlist saves, and invalid input 123. Both directions of
list/map selection and the health status are not clearly demonstrated; a
supplemental clip is still recommended. Audio was not assessed by the agent.
The older booking video covers a separate assignment.

[Verification record](assignment2-verification.md)
includes live ZIP 16802 observations, automated fixture instructions, expected
versus observed results, screenshots, SQLite evidence, and explicit limitations.

Suggested recording: show health status; search 16802; select a list item and
another marker; save a hotel twice to demonstrate duplicate protection; refresh;
restart the backend; show the retained shortlist; remove the item; then show
the fixture checks. Do not show terminals or editors containing credentials.

## AI disclosure and evidence log

Tool: OpenAI Codex desktop coding agent, with shell tools and browser automation.
**Specific selected model: GPT-6 Astra**, confirmed by the student on September 29, 2026. The agent
implemented provider normalization, SQLite shortlist operations, Vue/Leaflet UI,
mocked tests, and these draft notes. Browser observations were performed by the
agent and do not stand in for the student's personal review.

Selected prompt/decision evidence:

- Student requested completion of missing hotel search/map and persistent
  shortlist, then instructed the agent to continue. This maps to `places.py`,
  `shortlist.py`, `NearbyHotels.vue`, and `HotelMap.vue`.
- Student explicitly approved: “Approve installing Leaflet 1.9.4.” The exact
  install updated frontend/package.json and package-lock.json; the build passed.
- Earlier ZIP prompts required backend-only credentials and sanitized provider
  errors. The new Places controller reuses that configuration and HTTP capability.
- Revised approaches: test syntax correction, closing HTTP errors, and making
  the live results list scrollable are recorded in the verification notes.

Before submitting each part, review the implementation, confirm the assessed
commit, add any supplemental demonstration, and ensure every linked
artifact is published and accessible to the instructor. Upload the finalized
report as `report.md`. Screenshots alone do not satisfy the recorded-demo item.
