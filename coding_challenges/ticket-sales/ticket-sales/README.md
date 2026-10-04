# Challenge: Ticket sales database (data layer)

**Time box: about 75 minutes of work** (you have 48 hours to send it back). Please stop at about 90 minutes even if you're not finished, and tell us what you'd do next. We care more about clear, working code than about finishing everything.

## The situation

A small venue sells tickets online. Each order is for one event, from one buyer, for 1 to 10 tickets. Free tickets for staff and guests use the coupon `COMP`. Other coupons are just marketing tracking codes and don't change the price.

The data layer uses SQLite through Python's built-in `sqlite3` module, so there's nothing to install. Two of its reports are wrong, the orders table doesn't protect itself, and the code for selling tickets hasn't been written yet.

## What's already here

```
sales/schema.sql   events (done) and orders (works, but has no constraints)
sales/db.py        connect(), add_event() and two reports with bugs; place_order() and sales_report() are TODOs
tests/             A test database fixture, an insert_order() helper and a few starter tests
```

Setup (Python 3.11+):

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest            # 3 of the 4 starter tests fail until you finish tasks 1 and 3
```

## Your tasks

1. **Fix the two reports.** The box office says `average_order_size` reports **2** when orders of 2 and 3 tickets should average **2.5**, and `paid_orders` is missing every order that had no coupon. The failing tests show both. Fix them, and explain each cause in NOTES.md. Both are about how SQL behaves, not Python.

2. **Protect the `orders` table** in `sales/schema.sql`. The database itself, not just the Python code, should make sure that:
   - every order belongs to an event that exists, and an event that has orders can't be deleted
   - the buyer's email is always there and at least looks like an email (something `@` something)
   - the quantity is always 1 to 10
   - the unit price is always there and never negative
   - the created time is always filled in

   Also add an index that helps look up orders by event.

3. **Write `place_order` and `sales_report`** in `sales/db.py`:
   - **`place_order(conn, event_id, buyer_email, quantity, coupon=None)`**
     - Copies the event's current price into `unit_price_cents`, or uses 0 for the coupon `COMP`.
     - Raises `SoldOut` if the order would take sales over the event's capacity. Selling exactly the last tickets is fine.
     - Raises `LookupError` for an unknown event.
     - A refused order must not be saved, and two orders arriving together must never oversell. Think about transactions.
   - **`sales_report(conn)`** returns one row per event, sorted by name, **including events with no sales**: `event`, `tickets_sold`, `revenue_cents`, `remaining`.

4. **Tests.** Add tests for at least: a constraint the database now enforces, selling exactly the last tickets, a `COMP` order being free, and `sales_report` with an event that has no sales.

5. **`NOTES.md`** (5–10 lines): both bug causes, decisions you made, anything you'd change with more time, and roughly how long you spent.

## Ground rules

- Standard library plus `pytest` only. No ORM: we want to see the SQL.
- Documentation and search are fine. If you use an AI assistant, say where in NOTES.md. We'll ask you to walk through your code either way.
- Send it back as a zip or a link to a private GitHub repo. Please don't post it publicly.

## Optional, only if you have time left

Your schema changes only apply to brand-new databases, because of `CREATE TABLE IF NOT EXISTS`. Write a short migration (a SQL file or a Python function) that would add the constraints to an existing database without losing its orders.
