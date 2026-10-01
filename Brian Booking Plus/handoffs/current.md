# October 1 local hotel activity — ready for student manual checks

The original runtime folder now has additive local hotel/night tables and
Add to Local / Remove from Local controls. Search reads local data first;
only successful empty local lookup falls back to the unchanged Part 1 route.
All 31 backend tests, 5 frontend lookup tests, and build pass. Agent fixture
browser checks passed; no student DB Browser or Write Changes evidence is claimed.
See docs/local-storage-activity/manual-checklist.md and evidence.md.

Servers: frontend 5173, backend 8000; original database remains
backend/storage/expedia.sqlite3. Existing row fingerprints matched after migration.
The temporary fixture server on 8001 was stopped. No provider quota was consumed
by fixture checks, and no new dependency was installed.

The feature branch assignment2_part2_in_class is checked out in
C:/Users/kuane/AppData/Local/Temp/brian-booking-plus-assignment2-publish-20260929.
Selected changes are mirrored there, uncommitted for review. Runtime files and
saved database stay in the original Documents folder. Original checkout branch
is unchanged. No new code was pushed; published Part 1 remains preserved.
Next: student manually inspect DB Browser, perform live Add/Remove and Network
checks, edit a dated row, click Write Changes, repeat ZIP search, and capture evidence.

# Current handoff

## Working

Brian Booking Plus Part 2 provides SQLite hotel search, demo traveler selection, and frontend create/read/cancel/delete bookings. Initial startup seeds the four CSVs once; later startup preserves saved records. Local databases are excluded from Git. Part 1 remains preserved at db85ff8fe8b0a1b79c216fab49984c557342d440.

## Evidence

September 15 agent browser checks verified search, frontend CRUD, refresh, and restarting both servers. The screenshots and student-supplied MP4 are linked in report.md. The recording predates the rename from Expedia Lite. The student's recording is complete; a separate confirmation of their Part 2 VS Code source scan has not been recorded.

## Publication and next task

The publication branch codex/publish-part2 isolates Assignment 1 Part 2 from newer local Assignment 2 work. The feature branch was merged into main at 0743984eb768de1605ff62ed8fd0b4b33a4f35e3. All seven backend tests and the frontend build passed after merging on September 29. report.md records that application checkpoint; a follow-up documentation commit finalizes the report without changing the application. Keep newer ZIP/nearby-hotel files and personal database records in the local working project. Do not overwrite that work with the isolated publication checkout.

Confirm the required student source review, then upload report.md to Canvas. GitHub publication does not submit the assignment. The application is a local simulation without authentication, payments, or inventory enforcement. The test client emits an httpx deprecation notice.

## Local working folder

The published main branch is checked out in the separate temporary publication worktree. This original working folder remains on codex/part2-sqlite-crud with its newer uncommitted Assignment 2 work intact, including backend config/ZIP/places/shortlist modules and frontend NearbyHotels. Only the report and related status documentation were updated here. Do not blindly reset or overwrite this working folder when reconciling it with published main. Publication completed at commit 7fb9b52; the report identifies the application merge checkpoint separately.
# Assignment 2 local update — September 29, 2026

Hotel search within 5 km, synchronized Leaflet list/map, and persistent SQLite
shortlist are implemented locally. Leaflet 1.9.4 was explicitly approved and
installed. Backend tests (24) and frontend production build pass. Live ZIP
16802 returned usable hotels; save/page reload/backend restart/removal were
observed. The original hotel-name search still returns T001/T009 for Harbor
Lantern Hotel. See `docs/assignment2-verification.md` for evidence and limits,
and `docs/assignment2-report.md` for the separate submission draft.

Assignment 2 application commit `2a979ce81aa70b45c50f962c47b0ba2a27c0ee0e` was published to GitHub main at the student's explicit request. The older root
report/video remain for the previous booking assignment. Student video is linked in the Assignment 2 report. Supplemental list/map selection and health-status evidence, final student review, and model confirmation remain pending.
Backend and Vite are running on ports 8000 and 5173. Do not print `.env` or
provider request URLs. Preserve saved database and unrelated processes.
