# October 1 — your manual demonstration

Open the real app at **http://127.0.0.1:5173/** (backend: **http://127.0.0.1:8000**).
The temporary fixture server used by the agent is stopped. It is not your
submission demonstration. The app's older shortlist is separate: use **Add to
Local** and **Remove from Local** for this activity, not **Save hotel**/shortlist.

## Open the correct database

In DB Browser for SQLite choose **Open Database** and select:

```text
C:\Users\kuane\OneDrive\Documents\ChatGPT\Travel Application\Brian Booking Plus\backend\storage\expedia.sqlite3
```

Keep it on this path. The instructor's example path `backend/db/expedia.sqlite3`
does not apply to this project. The schema migration has run; the new tables
start empty. Existing hotels, trips, users, bookings, and earlier shortlist
records remain. If DB Browser already had the file open, reopen or refresh it.

## 1. Schema — 2 points

In **Database Structure**, inspect:

- `saved_hotels`: provider ID is `hotel_id` (primary key), nullable `name` and
  `address`, required valid `latitude` and `longitude`.
- `demo_hotel_nights`: composite primary key `(hotel_id, stay_date)`, foreign
  key to `saved_hotels`, defaults `nightly_rate_cents=10000`, `rooms_available=20`.
- `saved_hotel_zips`: links a hotel to searched ZIP(s); `saved_zip_locations`
  keeps the returned ZIP center separately from the hotel's address ZIP.
- Assignment 1 tables and supplied records. Before the migration this saved
  database had 8 hotels, 12 trips, 6 users, and 11 bookings (including previous
  activity changes). The agent's fingerprint comparison found them unchanged.

Compare an actual Part 1 response in Network with the old `hotels` table:
`place_id` is the external provider ID, whereas old `hotel_id` stores sample
IDs such as H001. `name` corresponds conceptually to `hotel_name`; the old
table lacks a full address, latitude, longitude, and date-specific inventory.
The API response has no nightly rate. The old sample price is not an API price.
Capture your own schema/row evidence.

## 2. Add and retain — 2 points

1. Open browser Developer Tools (F12), select **Network**, filter `api/`, and
   clear its request list. Search **16802** in **Explore nearby hotels**.
2. With no saved matches, expect **API results** and the returned hotel list/map.
3. Choose one hotel, note its name, and click **Add to Local**. Expect disabled
   **Saved locally** and an available **Remove from Local** button.
4. In DB Browser **Browse Data**, inspect `saved_hotels`, `saved_hotel_zips`,
   and `demo_hotel_nights`. Match the provider ID. Expect five dated rows for
   **2026-10-10 through 2026-10-14**, initially 10000 cents and 20 rooms each.
5. Refresh the web page and repeat the ZIP search. Expect **Saved locally**,
   disabled Add, and the same hotel/date records. Record what you see.

The UI prevents a duplicate Add; a duplicate API save is also idempotent and
covered by automated tests. To inspect that manually without extra provider
calls, replay the same local POST using your browser's supported Network
resend facility or localhost FastAPI docs, then check row counts and values.
Use the exact captured request body. Do not modify Part 1 provider URLs or keys.

## 4. Local-first requests — 2 points

Do this before removal:

- Clear Network and repeat a ZIP search that has saved hotels. Expect
  `GET /api/local-hotels?postcode=16802`, **Saved locally**, and no new
  `/api/hotels?postcode=16802` request.
- For a ZIP with no local matches, expect the local lookup returning
  `hotels: []`, then `/api/local-hotels/status`, then the original
  `/api/hotels?postcode=...` request and **API results**. You can use a second
  ZIP, or capture this during step 2 before the first save.
- Existing `/api/shortlist`, `/api/users`, and `/api/bookings` requests are
  unrelated to hotel-provider fallback. Map tile requests are also separate.
- If checking failure manually, block the local lookup request with your
  browser's Network request-blocking feature, repeat the search, and expect
  an error without a provider search. Remove the blocking rule afterward.
  Agent fixture checks already cover this; do not claim them as your manual check.

## 5. Edit, Write Changes, reread — 2 points

1. Keep your selected hotel saved. In DB Browser, filter `demo_hotel_nights`
   to that **hotel_id** and **2026-10-10**.
2. Record the before values: normally **10000 cents / 20 rooms**.
3. Change `nightly_rate_cents` to **12345** and `rooms_available` to **7**
   (or choose your own nonnegative integer values).
4. Click **Write Changes**. Merely editing the cells is not sufficient.
5. Return to the browser and repeat **16802**. Expect **Saved locally** and
   **$123.45 / 7 rooms** for the same hotel and **2026-10-10**. Other dates
   should retain their previous values. No app restart should be necessary.
6. Capture the committed row and matching frontend row. Record hotel name,
   provider ID, ZIP, date, and before/after values in `evidence.md`.

## 3. Remove a different saved hotel — 2 points

Use a second saved hotel so your comparison hotel remains available. If you
did not save a second hotel before local lookup took over, use another ZIP
with no saved hotels to obtain API results and add one there.

1. Record the second hotel's ID and its local related rows.
2. Click **Remove from Local** on its result card.
3. Expect the UI to update only after confirmation. For local results the
   card and marker disappear; for API results the card remains with Add enabled
   and no Remove button.
4. Refresh DB Browser. Confirm the selected hotel, its ZIP associations, and
   its nightly rows are gone. Confirm your comparison hotel and Assignment 1
   records remain. An unused ZIP-center row may be removed; shared ZIP centers
   remain if other saved hotels use them.

Record each benchmark's expected and observed results. State which, if any,
you personally demonstrated to the instructor/TA. Add screenshots or a recording
link; exclude API keys and `.env` contents. Stop here: no model integration.
