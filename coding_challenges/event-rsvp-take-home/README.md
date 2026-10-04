# Take-home: Event RSVP API + invoice bug hunt (backend)

Two short challenges sent together: **about 100 minutes of work in total.**

| Folder | Time | What it shows |
|---|---|---|
| `01-rsvp-api` | ~70 min | Building: Python, FastAPI, turning written rules into code, edge cases, HTTP status codes, tests |
| `02-invoice-bug-hunt` | ~30 min | Debugging someone else's code: float money, a mutable default argument, an off-by-one date range |

- **Send:** the pipeline sends `01-rsvp-api` and `02-invoice-bug-hunt` (challenge 1 in `challenges.json`). By hand, zip those two folders only.
- **Review:** `_reviewer_only/RUBRIC.md`. The reference solutions and reviewer tests are in the same folder.
- **Checked:** the starter fails 2 of its 3 tests, and the bug hunt fails 4 of 6. The reference passes all 21 tests (including the reviewer tests), and the bug-hunt fix passes all 6.
