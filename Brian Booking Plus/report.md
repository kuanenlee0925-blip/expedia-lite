# Brian Booking Plus — Part 2

## Repository and commit

Repository: [kuanenlee0925-blip/expedia-lite](https://github.com/kuanenlee0925-blip/expedia-lite) (public).

Part 2 was developed on a feature branch. An isolated publication branch, `codex/publish-part2`, contains the SQLite booking application and excludes newer Assignment 2 ZIP/nearby-hotel work. Part 2 application checkpoint: [0743984eb768de1605ff62ed8fd0b4b33a4f35e3](https://github.com/kuanenlee0925-blip/expedia-lite/commit/0743984eb768de1605ff62ed8fd0b4b33a4f35e3). This merge into `main` was checked on September 29, 2026. The final report is recorded in a follow-up documentation commit; the application code is unchanged.

Part 1 remains preserved as tag `part1`, commit [db85ff8fe8b0a1b79c216fab49984c557342d440](https://github.com/kuanenlee0925-blip/expedia-lite/commit/db85ff8fe8b0a1b79c216fab49984c557342d440). The completed [Part 1 report](https://github.com/kuanenlee0925-blip/expedia-lite/blob/0743984eb768de1605ff62ed8fd0b4b33a4f35e3/Brian%20Booking%20Plus/docs/part1-report.md) is archived separately.

## Implementation

Since Part 1, the application is now named Brian Booking Plus. Python uses SQLite for every application read and write. Initial startup creates hotels, trips, users, and bookings and imports the supplied CSV records in one transaction. A persistent seed marker prevents later startups from reloading, duplicating, or restoring starter records. Database foreign keys enforce relationships; existing IDs are preserved and new bookings receive unique UUID-based IDs.

Vue provides hotel-name search, a demo traveler selector, Book stay buttons, and history. FastAPI receives requests, validates IDs and status, and calls SQLite through parameterized queries. Creation adds a confirmed booking; history reads joined traveler/hotel/stay data; cancellation updates status while retaining the record; deletion removes a test booking after frontend confirmation. Dates and nightly rates determine nights and total price. Database files remain local and are excluded from Git.

## Verification

Agent browser and restart checks below were performed September 15, 2026. The student subsequently reported completing a recording and supplied the demonstration video linked below. A separate confirmation of the required Part 2 manual source scan in VS Code has not been recorded; this report does not mark that check complete.

| Action | Expected | Observed |
| --- | --- | --- |
| CHECK SQLite in the existing virtual environment; save, close, reopen a test row | Existing SQLite works and retains data | Passed: Python 3.14.7, SQLite 3.50.4; reopened value was saved; no SQLite installation needed |
| First startup | 8 hotels, 12 trips, 6 users, 6 bookings with original IDs | Passed; U001 showed B001 confirmed and B002 cancelled; U006 initially had no history |
| Search Harbor Lantern Hotel | T001 and T009, two nights at $150/night, $300 each | Passed in browser using the SQLite backend |
| Search No Such Hotel | Clear no-results message | Passed in browser |
| Create a T001 booking for U006 through Book stay | New ID and confirmed row in history | Passed: B-3d6533be9a1f463ea874446cda8492ee |
| Cancel that new booking through the frontend | Same ID remains, status cancelled | Passed |
| Create T009 for U006 | Additional confirmed booking beyond seed examples | Passed: B-db7b857420824db0bb570fc5f73bacb4 |
| Create and delete a separate test booking through the frontend | Test row removed; other bookings retained | Passed: B-bf39b01784034384b4d798056712efae removed |
| Refresh browser and reselect U006 | Addition and cancellation retained, deleted ID absent | Passed |
| Stop and restart both frontend and backend, refresh, reselect U006 | Same two new records and statuses, no duplicate seeds | Passed: confirmed T009 and cancelled T001 retained; deleted ID absent; all original B001–B006 unchanged |
| Additional screenshot example: create, cancel, delete B-ae8cff744243495291af4291d94fbfe8 through UI | Each action reflected in history | Passed; original verification records remain |
| Run backend unittest suite on temporary databases | Correct joins, CRUD, restart persistence, foreign keys, validation, concurrent unique IDs, and failed-seed rollback | Passed: 7 tests; also confirmed a deleted seed record is not restored and initialized storage does not need CSVs |
| Build Vue frontend | Successful compilation | Passed: npm run build |
| Student supplies personal demonstration | Accessible recording for instructor review | Completed: student supplied the September 15 MP4; published on GitHub |
| Student manually scans Part 2 changes in VS Code | Personal source review | Not separately confirmed in the recorded conversation |

September 29 publication checks: all seven backend tests passed again after the merge into `main`, using temporary databases. A clean frontend dependency install and production build passed; the merged frontend build also passed. The original Part 1 tag still resolves to the same implementation commit. Newer local Assignment 2 files, `.env`, personal databases, dependencies, and generated build output were excluded from this publication.

Evidence saved in the repository:

- [Persisted confirmed and cancelled bookings after server restart](https://github.com/kuanenlee0925-blip/expedia-lite/blob/0743984eb768de1605ff62ed8fd0b4b33a4f35e3/Brian%20Booking%20Plus/docs/screenshots/part2/07-after-restart.png).
- [Cancellation retains the new test record](https://github.com/kuanenlee0925-blip/expedia-lite/blob/0743984eb768de1605ff62ed8fd0b4b33a4f35e3/Brian%20Booking%20Plus/docs/screenshots/part2/10-cancel-history.png).
- [Deletion removes that test record](https://github.com/kuanenlee0925-blip/expedia-lite/blob/0743984eb768de1605ff62ed8fd0b4b33a4f35e3/Brian%20Booking%20Plus/docs/screenshots/part2/11-deleted-history.png).

The screenshots above are agent-operated browser evidence.

[Student demonstration video (MP4, approximately 21 MB)](https://github.com/kuanenlee0925-blip/expedia-lite/raw/a974d976c883a7a0e0286ae5a5eb74601ceaeacc/media/part2-demonstration.mp4). The recording and September 15 screenshots show the earlier Expedia Lite name; the published application is named Brian Booking Plus. Depending on the browser, the video opens or downloads. This report does not claim that every requirement was independently verified from the student recording.

## Project context and next steps

[README](https://github.com/kuanenlee0925-blip/expedia-lite/blob/0743984eb768de1605ff62ed8fd0b4b33a4f35e3/Brian%20Booking%20Plus/README.md), [AGENTS.md](https://github.com/kuanenlee0925-blip/expedia-lite/blob/0743984eb768de1605ff62ed8fd0b4b33a4f35e3/Brian%20Booking%20Plus/AGENTS.md), [design note](https://github.com/kuanenlee0925-blip/expedia-lite/blob/0743984eb768de1605ff62ed8fd0b4b33a4f35e3/Brian%20Booking%20Plus/docs/design.md), [selected prompts](https://github.com/kuanenlee0925-blip/expedia-lite/blob/0743984eb768de1605ff62ed8fd0b4b33a4f35e3/Brian%20Booking%20Plus/prompts/selected.md), [current handoff](https://github.com/kuanenlee0925-blip/expedia-lite/blob/0743984eb768de1605ff62ed8fd0b4b33a4f35e3/Brian%20Booking%20Plus/handoffs/current.md), and [student review checklist](https://github.com/kuanenlee0925-blip/expedia-lite/blob/0743984eb768de1605ff62ed8fd0b4b33a4f35e3/Brian%20Booking%20Plus/docs/review-checklist.md).

The app is a local classroom simulation without authentication, payments, room inventory, or capacity enforcement. Repeated intentional bookings are allowed. The traveler selection resets on page refresh; reselect the traveler to view saved records. A network timeout can leave a write's outcome uncertain, so the app refreshes history and advises checking before retrying. The test client emits a dependency deprecation notice; all tests pass.

Next: confirm the required personal VS Code review if it has not already been completed, then upload this updated report.md to Part 2 — Submission in Canvas. Publishing to GitHub does not submit the Canvas assignment. Accounts and personalized pricing from the later class activity are outside this Part 2 checkpoint.
