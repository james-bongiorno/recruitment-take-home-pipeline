# Take-home: Ticket sales database (data layer)

Fix two SQL reports, add real constraints to an orders table, and write a ticket sale that can't oversell, plus a sales report. The bugs are SQL classics: `!=` against NULL, and integer division in SQLite. Plain Python and `sqlite3`, no ORM. **About 75 minutes.**

- **Send:** the pipeline sends `ticket-sales/` (challenge 3 in `challenges.json`). By hand, zip `ticket-sales/`.
- **Review:** `_reviewer_only/RUBRIC.md`. The reference is in `_reviewer_only/ticket-sales/`, and `tests/test_reviewer.py` drops into their `tests/` folder.
- **Checked:** the starter fails 3 of its 4 tests. The reference passes all 22 (including the reviewer tests), and the untouched starter fails 21.
