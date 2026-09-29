# Part 2: student review and demonstration

The student supplied the demonstration recording. Use this checklist for the required source review and for any checks you want to repeat. Agent browser evidence is recorded separately in report.md; student source review has not been separately confirmed.

## 1. Review in VS Code

Open the Travel Application workspace. Use the Part 2 application checkpoint linked in report.md; newer local Assignment 2 work may contain additional files. Review:

- backend/database.py: tables, foreign keys, transaction, and the one-time seed marker.
- backend/main.py: SQLite search plus create, history, cancel, and delete endpoints.
- frontend/src/App.vue: traveler selector, Book stay, history, cancellation, and delete confirmation.
- backend/test_app.py: tests use temporary databases rather than your saved data.
- README.md and report.md: setup, observed checks, and remaining steps.

## 2. Demonstrate through the browser

1. Open http://127.0.0.1:5173 and select **Demo Traveler 5 (U005)**. Its original B006 is already cancelled; leave that starter row alone.
2. Search **Harbor Lantern Hotel**. Expect T001 and T009, each $300. Also try **No Such Hotel** and check the no-results message, then search Harbor Lantern again.
3. Click **Book stay** for **Boston Harbor Weekend (T001)**. Find the new confirmed row in history and note its booking ID.
4. Click **Cancel booking** on that new row. Expect the same ID with status **cancelled**.
5. Book **Boston Autumn Weekend (T009)**. Keep this new booking confirmed and note its ID.
6. Book **Boston Harbor Weekend** once more as a disposable test. Note the new ID, then choose **Delete booking → Confirm delete** for that row. Expect it to disappear.
7. Refresh the browser and reselect Traveler 5. Expect B006 plus your cancelled T001 and confirmed T009; the deleted test ID should be absent.
8. Tell the agent you reached this step. It can restart both servers, then you should refresh, reselect Traveler 5, and confirm the same records/statuses remain. If restarting yourself, stop both terminals with Ctrl+C and use README's Run commands again.

Record your expected and observed results. Tell the agent about any mismatch; do not report a check as passed if it did not pass.

## 3. Complete the Git checkpoint and submission

The GitHub report records the publication checkpoint and accessible evidence. After completing your required review, upload the updated report.md to **Part 2 — Submission** in Canvas.
