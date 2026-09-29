# Brian Booking Plus design

Vue owns hotel search, demo traveler selection, booking actions, history, and loading/error messages. Vite forwards `/api` requests to FastAPI on port 8000. The frontend never reads CSVs or opens the database directly.

FastAPI validates inputs and exposes GET /api/stays, GET /api/users, GET /api/bookings?user_id=..., POST /api/bookings, PATCH /api/bookings/{id}, and DELETE /api/bookings/{id}. Creation returns 201; deletion returns 204; unknown references or records return 404; malformed bodies return 422. Updates accept only the cancelled status, retaining the row. All bookings are simulated and can be deleted after the frontend confirmation.

Python joins hotels/trips on hotel_id, then bookings/users/trips for history. It calculates nights and price from the stored dates and rate. Parameterized SQL handles all request values. Search uses a casefold function and literal substring matching, so % and _ are ordinary characters. An empty query lists all stays. IDs and fixed dates retain the supplied model.

database.py opens short-lived SQLite connections with foreign-key enforcement and commits writes transactionally. A BEGIN IMMEDIATE transaction creates the schema, imports the four CSVs, and sets PRAGMA user_version=1 together. A failed seed rolls back; a later startup retries. Version 1 bypasses CSV reads entirely, including when bookings have been deleted. Database and CSV paths default to locations relative to the backend source; an explicit database path supports isolated tests. New bookings use UUID-based IDs protected by a primary key. Concurrent writes serialize through SQLite.

Vue blocks repeated pending mutations and traveler changes during a write. History requests use a sequence number so a slower response cannot overwrite another traveler's data. Requests time out after 20 seconds; after uncertain mutations the app refreshes history and advises checking it before retrying. Repeated intentional bookings are allowed; automatic POST retries are not used.

The app is local and has no authentication, payment, room inventory, capacity limits, or booking reactivation. The demo traveler selector is not an authorization boundary. Sample dates are fixed and are not filtered by today's date. No calculator starter was present originally. Part 1 remains preserved in Git.
