# Assignment 2 — Part 1: Live Hotel Search and Map

Brian Booking Plus · September 29, 2026

This submission concerns ZIP-based live hotel search and synchronized list/map selection. The same application also contains shortlist work for Part 2; that extra functionality does not replace Part 1 evidence. Final student review remains pending, as noted below.

## 1. Project access, startup, and configuration

- [Public repository](https://github.com/kuanenlee0925-blip/expedia-lite)
- **Assessed application commit:** [2a979ce81aa70b45c50f962c47b0ba2a27c0ee0e](https://github.com/kuanenlee0925-blip/expedia-lite/commit/2a979ce81aa70b45c50f962c47b0ba2a27c0ee0e)
- [Complete setup documentation](https://github.com/kuanenlee0925-blip/expedia-lite/blob/2a979ce81aa70b45c50f962c47b0ba2a27c0ee0e/Brian%20Booking%20Plus/README.md)

Check out the assessed commit and open its `Brian Booking Plus` directory. Prerequisites: Python 3.10+ and Node 22.12+. For a fresh environment, use Windows PowerShell:

```powershell
python -m venv backend/.venv
backend\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
npm.cmd --prefix frontend ci
```

Configure a private `GEOAPIFY_API_KEY` in the project-root `.env`, beside `frontend/` and `backend/`. The file is ignored. `backend/config.py` loads its explicit path; a process environment variable takes precedence. Restart the backend after changing it. No credential value or `.env` contents are included in this report.

Start the backend in one terminal:

```powershell
backend\.venv\Scripts\python.exe -m uvicorn main:app --app-dir backend --host 127.0.0.1 --port 8000
```

In another terminal, from the same project directory:

```powershell
npm.cmd --prefix frontend run dev
```

Open `http://127.0.0.1:5173/`. Vite proxies `/api` to FastAPI on port 8000. `http://127.0.0.1:8000/api/health` reported **key is configured** during the September 29 verification. This reports configuration presence, not provider key validity. Live searches separately confirmed usable provider data.

A five-digit ZIP string flows from [NearbyHotels.vue](https://github.com/kuanenlee0925-blip/expedia-lite/blob/2a979ce81aa70b45c50f962c47b0ba2a27c0ee0e/Brian%20Booking%20Plus/frontend/src/NearbyHotels.vue) to the [FastAPI route](https://github.com/kuanenlee0925-blip/expedia-lite/blob/2a979ce81aa70b45c50f962c47b0ba2a27c0ee0e/Brian%20Booking%20Plus/backend/main.py), then [places.py](https://github.com/kuanenlee0925-blip/expedia-lite/blob/2a979ce81aa70b45c50f962c47b0ba2a27c0ee0e/Brian%20Booking%20Plus/backend/places.py) and [zip_lookup.py](https://github.com/kuanenlee0925-blip/expedia-lite/blob/2a979ce81aa70b45c50f962c47b0ba2a27c0ee0e/Brian%20Booking%20Plus/backend/zip_lookup.py). The backend verifies the exact requested U.S. postcode before searching Geoapify for `accommodation.hotel` within 5,000 meters of that returned point. It normalizes returned fields for the Vue list and [HotelMap.vue](https://github.com/kuanenlee0925-blip/expedia-lite/blob/2a979ce81aa70b45c50f962c47b0ba2a27c0ee0e/Brian%20Booking%20Plus/frontend/src/HotelMap.vue). The center is not the traveler's location. Each provider request has a 10-second timeout; Vue has a 30-second timeout.

The result limit is **20**, not an exhaustive inventory. Missing names/addresses receive honest labels; invalid coordinates and outside-radius places are omitted. Provider data does not establish room availability, prices, or ratings. Geoapify requests and the private key remain in FastAPI. Leaflet uses standard OpenStreetMap tiles with visible attribution and no backend credential.

## 2. Research notes and resulting decisions

Research was performed by the coding agent using documentation before implementation. These notes do not claim that the student personally tested competing applications.

| Source | Useful observation | Weakness or limitation for this project | Adopted decision |
| --- | --- | --- | --- |
| [Airbnb search help](https://www.airbnb.com/help/article/479) | Accommodation search combines location, maps, and ways to narrow results. | Price, date, and availability filters need data our location API does not establish; a help article is not a hands-on comparison. | Use one ZIP control and a paired list/map; omit invented booking information. |
| [Geoapify Geocoding](https://apidocs.geoapify.com/docs/geocoding/) | Structured postcode lookup and country filtering support U.S. ZIP resolution. | A returned candidate must still match the requested postcode. | Validate exact postcode, U.S. country, and usable coordinates before searching hotels. |
| [Geoapify Places](https://apidocs.geoapify.com/docs/places/) | Categories and geographic filters support nearby hotel discovery. | Coverage and optional fields vary; places are not bookable room inventory. | Use hotel category, 5 km circle, 20-result cap, coordinate checks, and missing-field labels. |
| [Leaflet reference](https://leafletjs.com/reference.html) | Markers, events, popups, and attribution support a connected map. | Leaflet supplies map interaction, not hotel records or map imagery. | Share selected place ID between list and map; use a separate tile provider. |
| [Geoapify pricing and usage](https://www.geoapify.com/pricing/) | Service quotas make repeated live requests a resource to manage. | Provider limits and actual costs can change. | Search only on submit; mock empty/error/rate-limit cases; do not search again on map movement. |
| [OpenStreetMap tile policy](https://operations.osmfoundation.org/policies/tiles/) | Standard interactive tiles can provide the map background with attribution and normal caching. | Public tiles have usage restrictions and are not an unlimited bulk-download service. | Retain attribution, use browser caching, and avoid prefetch or bulk downloads. |

[Original research and design record](https://github.com/kuanenlee0925-blip/expedia-lite/blob/2a979ce81aa70b45c50f962c47b0ba2a27c0ee0e/Brian%20Booking%20Plus/docs/assignment2-research-and-design.md).

## 3. Early mockup and implementation revisions

[Open the early mockup](https://github.com/kuanenlee0925-blip/expedia-lite/blob/2a979ce81aa70b45c50f962c47b0ba2a27c0ee0e/Brian%20Booking%20Plus/docs/assignment2-early-mockup.svg).

![Early mockup prepared before hotel/map implementation](https://raw.githubusercontent.com/kuanenlee0925-blip/expedia-lite/2a979ce81aa70b45c50f962c47b0ba2a27c0ee0e/Brian%20Booking%20Plus/docs/assignment2-early-mockup.svg)

The September 29 mockup was prepared before hotel retrieval, Leaflet, and shortlist implementation. It uses fictional example hotels and a conceptual map placeholder, not real provider evidence. For Part 1, its relevant design is the ZIP control above adjacent list/map views, with loading/error/empty states. The shortlist portion anticipates Part 2.

After observing a live 20-result response, the results list was given a maximum height and scrolling to keep the map visible. The footer was clarified to distinguish fictional sample bookings from provider locations. These revisions retain the original list/map interaction.

## 4. Screen-recorded demonstration

[Watch/download the student's demonstration — MP4, about 55 seconds](https://github.com/kuanenlee0925-blip/expedia-lite/raw/refs/heads/main/media/assignment2-part1-demonstration.mp4).

Recorded September 29, 2026. Approximate timeline from the reviewed visual frames:

- 10–15 seconds: submit **16802**, show loading and State College hotel results/map.
- 16–30 seconds: save returned hotels and show the shortlist (additional Part 2 behavior).
- 35–41 seconds: submit **33647**, show loading and Tampa hotel results/map.
- 50–54 seconds: enter **123** and show browser validation feedback.

The clip does **not clearly demonstrate both directions of list/map selection or the health status**. Those selection actions were separately observed by the agent, as recorded below; a supplemental recording is recommended to strengthen the video evidence. Audio was not assessed. The uploaded MP4 was verified publicly downloadable without authentication.

## 5. Verification record

Live observations are dated **September 29, 2026**. Counts below describe that observation, not a test that assumes future provider results stay constant.

| Input/action | Expected result | Observed result and evidence |
| --- | --- | --- |
| Live search 16802 | Exact U.S. ZIP center, nearby hotels and matching map markers | Agent observed 20 returned hotels; student video also shows State College results. |
| Live search 33647 | Results/map change to the entered ZIP | Student video shows three Tampa hotel results. |
| Submit search | Visible loading; no repeated submission while pending | Loading state is visible in the recording; implementation disables pending search. |
| Select list item 2 | Map identifies Hotel State College | Agent observed matching selected list state and map popup. |
| Select marker 3 | List identifies Nittany Lion Inn | Agent observed matching selection and popup. Not clearly shown in student video. |
| Enter 123 and submit | Reject invalid ZIP | Browser displays validation feedback near the end of the recording. |
| Leading-zero ZIP route test | Preserve ZIP as a string | Mocked route test passed. Not a live leading-zero provider demonstration. |
| Unresolved/mismatched ZIP | No different-location hotel search | Mocked controller checks passed; unresolved ZIP avoids the Places call. |
| Empty features / malformed response | Empty success / provider error remain distinct | Backend mocked checks passed. Browser rendering of these simulated cases was not verified. |
| Simulated provider HTTP 500 / 429 | Safe provider failure / rate-limit response | Mocked checks passed; raw provider exception text excluded. |
| Missing fields / outside-radius fixture record | Honest missing fields; invalid location omitted | Fixed-fixture checks passed. |
| GET /api/health | Configuration status without key value | Observed `key is configured`. Not included in student clip. |
| Existing search: Harbor Lantern Hotel | Existing sample search preserved | Agent observed T001 and T009, each $300. |
| Automated suite and frontend build | No regression in checked behavior | All 24 backend tests and Vite production build passed. |

[Live map screenshot](https://github.com/kuanenlee0925-blip/expedia-lite/blob/2a979ce81aa70b45c50f962c47b0ba2a27c0ee0e/Brian%20Booking%20Plus/docs/screenshots/assignment2/01-live-map.png) and [detailed verification record](https://github.com/kuanenlee0925-blip/expedia-lite/blob/2a979ce81aa70b45c50f962c47b0ba2a27c0ee0e/Brian%20Booking%20Plus/docs/assignment2-verification.md).

Repeat automated checks from the project directory. A fresh test environment additionally needs `backend/requirements-dev.txt`; inspect existing dependencies before installing:

```powershell
backend\.venv\Scripts\python.exe -m pip install -r backend/requirements-dev.txt
Push-Location backend
.\.venv\Scripts\python.exe -m unittest discover -v
Pop-Location
npm.cmd --prefix frontend run build
```

Tests use mocked provider calls and temporary databases, avoiding provider quota consumption and changes to saved student data. The installed Starlette test client emits a deprecation notice; tests passed with the existing pinned dependency.

Corrections: an extra closing parenthesis in the new test was fixed before rerunning; HTTPError objects were explicitly closed to avoid resource warnings that might include provider URLs; the long list was made scrollable. Remaining limitations: no complete keyboard-only journey, narrow-screen visual check, or browser Network-panel credential inspection was recorded. Backend error tests are not a claim that all error states were exercised visually. Live coverage may change. No Canvas submission or instructor review is claimed.

## 6. AI disclosure and evidence log

**AI tool:** OpenAI Codex desktop coding agent. **Specific selected model: GPT-6 Astra**, confirmed by the student on September 29, 2026.

| Tool/capability | Use |
| --- | --- |
| Codex coding agent | Planned and implemented Vue/FastAPI changes, read documentation, wrote tests and report drafts, and diagnosed failures. |
| Shell, Python unittest, npm/Vite, Git | Inspected files/dependencies, ran checks, and published student-authorized changes and evidence. These are execution tools, not separate AI models. |
| Browser automation | Checked the running UI, selection correspondence, existing search, and screenshots. |
| Windows video APIs and Python image tools | Extracted frames to inspect the student recording; did not generate the student's demonstration or assess its audio. |

Selected student prompt excerpts and resulting evidence:

| Prompt excerpt | Resulting change, decision, or verification |
| --- | --- |
| “Read the API key through the configuration helper and supply it only in the backend request.” | [Configuration helper](https://github.com/kuanenlee0925-blip/expedia-lite/blob/2a979ce81aa70b45c50f962c47b0ba2a27c0ee0e/Brian%20Booking%20Plus/backend/config.py), [ZIP controller](https://github.com/kuanenlee0925-blip/expedia-lite/blob/2a979ce81aa70b45c50f962c47b0ba2a27c0ee0e/Brian%20Booking%20Plus/backend/zip_lookup.py), and reused backend HTTP/configuration in [Places controller](https://github.com/kuanenlee0925-blip/expedia-lite/blob/2a979ce81aa70b45c50f962c47b0ba2a27c0ee0e/Brian%20Booking%20Plus/backend/places.py). |
| “Distinguish an unresolved ZIP from a failed provider request.” | [Route translation](https://github.com/kuanenlee0925-blip/expedia-lite/blob/2a979ce81aa70b45c50f962c47b0ba2a27c0ee0e/Brian%20Booking%20Plus/backend/main.py) and [mocked ZIP tests](https://github.com/kuanenlee0925-blip/expedia-lite/blob/2a979ce81aa70b45c50f962c47b0ba2a27c0ee0e/Brian%20Booking%20Plus/backend/test_zip_lookup.py) distinguish unresolved and failure behavior. |
| “Keep the existing hotel-name search working.” | Existing search was retained in [App.vue](https://github.com/kuanenlee0925-blip/expedia-lite/blob/2a979ce81aa70b45c50f962c47b0ba2a27c0ee0e/Brian%20Booking%20Plus/frontend/src/App.vue); regression observation is recorded above. |
| “Approve installing Leaflet 1.9.4.” | Exact dependency added to [package.json](https://github.com/kuanenlee0925-blip/expedia-lite/blob/2a979ce81aa70b45c50f962c47b0ba2a27c0ee0e/Brian%20Booking%20Plus/frontend/package.json) after approval; frontend build verified it. |
| “keep going” after discussion of missing hotel/map and shortlist work | Implemented [NearbyHotels.vue](https://github.com/kuanenlee0925-blip/expedia-lite/blob/2a979ce81aa70b45c50f962c47b0ba2a27c0ee0e/Brian%20Booking%20Plus/frontend/src/NearbyHotels.vue), [HotelMap.vue](https://github.com/kuanenlee0925-blip/expedia-lite/blob/2a979ce81aa70b45c50f962c47b0ba2a27c0ee0e/Brian%20Booking%20Plus/frontend/src/HotelMap.vue), and provider controller, following the early mockup. |
| “is this video good enough” | Agent inspected visual frames and identified missing clear list/map selection evidence; this report does not claim the clip proves those steps. |

Failed/revised approach: the new [test_places.py](https://github.com/kuanenlee0925-blip/expedia-lite/blob/2a979ce81aa70b45c50f962c47b0ba2a27c0ee0e/Brian%20Booking%20Plus/backend/test_places.py) initially had an extra closing parenthesis; it was corrected and tests rerun successfully. The initial unrestricted result-list height also made the 20-result page too long; the View was revised to scroll alongside the map. These are actual corrections, not hypothetical examples.

The student supplied the recording and authorized dependency installation and GitHub publication. Agent verification is identified separately from student demonstration. Before submission, the student must review this report and decide whether to add the recommended supplemental clip. No full chat export or credentials are included.
