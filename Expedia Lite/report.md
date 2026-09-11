# Expedia Lite — Part 1

## Repository and commit

Repository: [kuanenlee0925-blip/expedia-lite](https://github.com/kuanenlee0925-blip/expedia-lite).

Part 1 implementation checkpoint: [db85ff8fe8b0a1b79c216fab49984c557342d440](https://github.com/kuanenlee0925-blip/expedia-lite/commit/db85ff8fe8b0a1b79c216fab49984c557342d440) (preserved by the `part1` tag). The report is finalized in a follow-up documentation commit; the reviewed application is unchanged.

This repository is private. The instructor must have repository access to open the linked source and screenshots.

## Implementation

Expedia Lite uses a Vue frontend to collect a hotel name and display offered stays in a table. Requests pass through FastAPI to a Python backend that reads hotels.csv and trips.csv and joins them using hotel_id. Search supports full or partial hotel names, ignores capitalization and surrounding spaces, and shows all stays for a blank query. The table includes location, hotel/trip IDs, dates, nights, nightly USD rate, and calculated stay price. Empty and failed searches have clear messages.

The supplied data and IDs are preserved. No calculator starter was present in the workspace, so the app was created from scratch. Booking and SQLite are reserved for Part 2.

## Verification

Agent-operated browser checks on September 11, 2026, using the running Vue and FastAPI servers:

| Action | Expected | Observed |
| --- | --- | --- |
| Search `Harbor Lantern Hotel` using Search button | T001 and T009, two nights each at $150/night, total $300 each | Passed: two correct rows with dates and prices |
| Search `No Such Hotel` | No rows; clear no-results message | Passed: “0 stays found” and a message suggesting another hotel name |
| Search `  hArBoR  ` | Same two rows despite spaces and case | Passed: T001 and T009 |
| Search with blank input | All 12 offered stays | Passed: “12 stays found” and 12 rows |
| Verify dependency imports | FastAPI/Uvicorn import in local virtual environment | Passed: FastAPI 0.141.1, Uvicorn 0.52.4 |
| Run frontend production build | Successful Vue compilation | Passed: Vite build completed |
| Student manually scans changes in VS Code | Student reviews and understands source changes | Completed: student confirmed the VS Code review and both required browser searches |

[Successful hotel search screenshot](https://github.com/kuanenlee0925-blip/expedia-lite/blob/db85ff8fe8b0a1b79c216fab49984c557342d440/Expedia%20Lite/docs/screenshots/search-match.png)

[No matching hotels screenshot](https://github.com/kuanenlee0925-blip/expedia-lite/blob/db85ff8fe8b0a1b79c216fab49984c557342d440/Expedia%20Lite/docs/screenshots/search-empty.png)

The linked screenshots are stored in the repository at the preserved Part 1 checkpoint. Sign in with an account that has access to view them.

## Project context and next steps

Project context: [README](https://github.com/kuanenlee0925-blip/expedia-lite/blob/db85ff8fe8b0a1b79c216fab49984c557342d440/Expedia%20Lite/README.md), [AGENTS.md](https://github.com/kuanenlee0925-blip/expedia-lite/blob/db85ff8fe8b0a1b79c216fab49984c557342d440/Expedia%20Lite/AGENTS.md), [design note](https://github.com/kuanenlee0925-blip/expedia-lite/blob/db85ff8fe8b0a1b79c216fab49984c557342d440/Expedia%20Lite/docs/design.md), [selected prompts](https://github.com/kuanenlee0925-blip/expedia-lite/blob/db85ff8fe8b0a1b79c216fab49984c557342d440/Expedia%20Lite/prompts/selected.md), and [current handoff](https://github.com/kuanenlee0925-blip/expedia-lite/blob/db85ff8fe8b0a1b79c216fab49984c557342d440/Expedia%20Lite/handoffs/current.md).

The student confirmed completion of the guided VS Code review and successful/no-results browser checks. Before submission, give the instructor access to the private repository and verify the links with them, then upload this report to Part 1 — Submission. The app is limited to fictional hotel search with fixed dates and sample rates; no real inventory or reservations exist. After preserving the Part 1 checkpoint, the next implementation task is Part 2 on a feature branch: seed SQLite once and add persistent simulated booking CRUD through the frontend.
