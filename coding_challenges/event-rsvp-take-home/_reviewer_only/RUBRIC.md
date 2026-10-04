# Reviewer rubric: Event RSVP API + invoice bug hunt

Score each row 0–2. A strong junior lands around 12+ of 18. Spend most of the follow-up call on their own walkthrough.

| Area | 0 | 1 | 2 |
|---|---|---|---|
| **1. Rules** | Don't run | Most rules right | All right, including normalized emails, duplicates on the waitlist, and skipping a party that doesn't fit |
| **1. API** | Missing | Works, wrong status codes | 201 / 400 / 404 / 409 correct, clear error messages |
| **1. Tests** | None added | The 4 asked for | Meaningful extras (exactly full, cancelling a waitlisted RSVP, emails with odd case) |
| **1. Code clarity** | Hard to follow | Readable | Small functions, rules easy to find, no duplicated seat counting |
| **2. Bugs fixed** | 0–1 | 2 | All 3 (float cents, mutable default, inclusive end date) |
| **2. Minimal fixes** | Rewrote the file | Some churn | Surgical fixes, tests untouched |
| **2. Own test** | None | Present | Would clearly have caught a real bug |
| **Notes** | Missing | Lists what they did | Honest time spent, trade-offs, next steps, AI use disclosed |
| **Git / hygiene** | Messy | Clean | Sensible commits on a branch, PR description that explains the work |

## Answer key

- **Challenge 1:** `01-rsvp-api/app/rsvps.py` and `app/main.py` in this folder. Copy `01-rsvp-api/tests/test_reviewer.py` into their `tests/` folder and run `pytest`.
- **Challenge 2:** `02-invoice-bug-hunt/invoices.py`. The three bugs:
  1. `int(float("19.99") * 100)` is 1998, because the float is 1998.999… and `int()` truncates. Fix with `Decimal`, or at least `round()`.
  2. `def new_invoice(customer, lines=[])`: the default list is created once, so every invoice made without lines shares it. Fix with `lines=None`.
  3. `invoices_between` uses `< end`, which leaves out the last day. Fix with `<= end`.

## Follow-up call questions

- Walk me through `cancel()`. Why does the order of the waitlist matter?
- Two RSVPs for the last seat arrive at the same moment. What happens? (Good answers: a transaction or lock, or a unique and capacity check in the database.)
- Why are prices kept in cents? What else could go wrong with money as floats?
- How did you find the mutable default bug? Had you seen it before?
