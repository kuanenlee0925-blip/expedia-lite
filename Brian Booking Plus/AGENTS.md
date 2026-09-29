# Brian Booking Plus

- Keep Vue in frontend/ and Python/FastAPI in backend/.
- Part 2 uses SQLite after a transactional one-time CSV seed. Never reseed an initialized database on startup.
- Preserve starter data and existing IDs. Keep the Part 1 tag and commit unchanged.
- All booking CRUD must be available through Vue and FastAPI. Cancellation retains the history row.
- Use parameterized SQL, enforce foreign keys, and keep database files out of Git.
- Run backend tests on temporary databases, never on the student's saved database.
- Check installed dependencies before adding any; install in the project environment, then verify imports/builds.
- Keep setup, design, report, prompts, and handoff consistent with actual behavior.
- Record actual checks; never claim human review, browser evidence, commits, or pushes that did not happen.
- Before a Git checkpoint, have the user review the work. Preserve the Part 1 commit when developing Part 2 on a feature branch.
