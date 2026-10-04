# Reviewer rubric: Ticket sales database

Score each row 0–2. A strong junior lands around 12+ of 18. Spend most of the follow-up call on their own walkthrough.

| Area | 0 | 1 | 2 |
|---|---|---|---|
| **Bug 1: integer division** | Not fixed, or fixed in Python | Fixed in SQL | Fixed with `AVG()` or `* 1.0`, and they explain that SQLite divides integers as integers |
| **Bug 2: NULL comparison** | Not fixed | Fixed | Fixed with `IS NOT` / `IS NULL OR`, and they explain three-valued logic (`NULL != 'COMP'` is NULL, not true) |
| **Constraints** | Missing, or only checked in Python | Some | FK without cascade, `NOT NULL`s, `CHECK (quantity BETWEEN 1 AND 10)`, email check, price `>= 0`, index on `event_id` |
| **place_order** | Doesn't work | Works, but check-then-insert isn't atomic | Price copied, COMP free, `SoldOut` at exactly capacity, wrapped in a transaction (`BEGIN IMMEDIATE` or similar), refused orders not saved |
| **sales_report** | Missing | Works, but leaves out events with no sales, or runs one query per event | `LEFT JOIN` + `COALESCE`, sorted, correct revenue |
| **Tests** | None added | The 4 asked for | Meaningful extras (sold-out order not saved, saving to a file, the email check) |
| **SQL style** | String-built SQL | Fine | Parameters everywhere, readable queries, named columns |
| **Notes** | Missing | Lists what they did | Honest time spent, trade-offs, next steps, AI use disclosed |
| **Git / hygiene** | `.db` files committed | Clean | Sensible commits, PR description explains the work |

## Answer key

- `ticket-sales/sales/schema.sql` and `ticket-sales/sales/db.py` in this folder are one reasonable answer.
- Copy `ticket-sales/tests/test_reviewer.py` into their `tests/` folder and run `pytest`. The reference passes all 22 tests, and the untouched starter fails 21.
- **Bug 1:** `SUM(quantity) / COUNT(*)` with two integers is integer division in SQLite, so 5 / 2 is 2. Fix with `AVG(quantity)`, which also returns NULL (None) when there are no rows.
- **Bug 2:** `coupon != 'COMP'` is NULL when `coupon` is NULL, and `WHERE` only keeps true rows, so orders with no coupon vanish. Fix with `coupon IS NOT 'COMP'` (SQLite) or `(coupon IS NULL OR coupon <> 'COMP')`, which works everywhere.
- **Transactions:** Python's `sqlite3` opens transactions implicitly by default, so a hand-written `BEGIN` can fail with "cannot start a transaction within a transaction." Working it out (with `isolation_level=None`, or by checking and inserting inside one `with conn:` block) is a good sign.

## Follow-up call questions

- What could go wrong if two people buy the last tickets at the same moment? How does your code prevent it? What changes on Postgres? (`SELECT … FOR UPDATE`, or a counter column with a `CHECK`)
- Why copy the price onto the order instead of joining to `events.price_cents` for the report?
- Why no `ON DELETE CASCADE` here, when it's common elsewhere?
- How would you check the sales report stays fast with a million orders? (`EXPLAIN QUERY PLAN`, the index on `event_id`)
