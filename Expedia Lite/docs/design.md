# Expedia Lite design

The Vue frontend owns the hotel-name input, Search button, loading/error/empty messages, and a results table. It sends a GET request to `/api/stays?hotel_name=...` and renders the returned records. The local Vite proxy forwards this route to port 8000.

FastAPI defines the HTTP endpoint and validates the query length and response structure. The Python backend reads hotels.csv and trips.csv with UTF-8 BOM support, filters hotel names using trimmed case-insensitive substring matching, and joins trips to matching hotels by hotel_id. It computes nights from checkout minus check-in, then multiplies by the supplied integer USD nightly rate. CSV paths are resolved relative to the source file, not the terminal's working directory.

An empty query lists every offered stay; unmatched names return an empty JSON array. The frontend keeps a snapshot of the submitted query so editing the input does not relabel existing results. Requests time out after ten seconds and failures show a retry message. Only one search can run at a time.

This is a local Part 1 app, with no database, authentication, payment, booking, or inventory tracking. The supplied users and bookings are retained for Part 2. The provided data guide's city examples do not override the assignment's hotel-name search requirement. No calculator starter was present, so this implementation was created in the empty workspace.
