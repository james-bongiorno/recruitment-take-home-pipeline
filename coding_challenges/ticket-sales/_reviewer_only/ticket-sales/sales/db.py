"""Reference solution (reviewer only).

Bugs in the starter:
  1. average_order_size: SUM(quantity) / COUNT(*) is integer division in SQLite (5 / 2 = 2).
     Fix: AVG(quantity), or SUM(quantity) * 1.0 / COUNT(*).
  2. paid_orders: `coupon != 'COMP'` is NULL (not true) when coupon is NULL, so orders with no
     coupon disappear. Fix: `coupon IS NOT 'COMP'`, or `(coupon IS NULL OR coupon != 'COMP')`.
"""
import sqlite3
from pathlib import Path

SCHEMA = Path(__file__).with_name("schema.sql")
COMP = "COMP"


class SoldOut(Exception):
    """Not enough tickets left for this order."""


def connect(path: str = ":memory:") -> sqlite3.Connection:
    conn = sqlite3.connect(path, isolation_level=None)  # we manage transactions ourselves
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA.read_text())
    return conn


def add_event(conn: sqlite3.Connection, name: str, capacity: int, price_cents: int) -> int:
    cur = conn.execute("INSERT INTO events (name, capacity, price_cents) VALUES (?, ?, ?)",
                       (name, capacity, price_cents))
    return cur.lastrowid


def average_order_size(conn: sqlite3.Connection, event_id: int) -> float | None:
    return conn.execute("SELECT AVG(quantity) FROM orders WHERE event_id = ?", (event_id,)).fetchone()[0]


def paid_orders(conn: sqlite3.Connection, event_id: int) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM orders WHERE event_id = ? AND coupon IS NOT ? ORDER BY id", (event_id, COMP)
    ).fetchall()
    return [dict(r) for r in rows]


def place_order(conn: sqlite3.Connection, event_id: int, buyer_email: str, quantity: int,
                coupon: str | None = None) -> int:
    # BEGIN IMMEDIATE takes the write lock now, so no one can sell the same seats
    # between our capacity check and our insert.
    conn.execute("BEGIN IMMEDIATE")
    try:
        event = conn.execute(
            """SELECT e.capacity, e.price_cents, COALESCE(SUM(o.quantity), 0) AS sold
               FROM events e LEFT JOIN orders o ON o.event_id = e.id
               WHERE e.id = ? GROUP BY e.id""", (event_id,)
        ).fetchone()
        if event is None:
            raise LookupError(f"No event with id {event_id}")
        if event["sold"] + quantity > event["capacity"]:
            raise SoldOut(f"Only {event['capacity'] - event['sold']} ticket(s) left")
        price = 0 if coupon == COMP else event["price_cents"]
        cur = conn.execute(
            "INSERT INTO orders (event_id, buyer_email, quantity, unit_price_cents, coupon)"
            " VALUES (?, ?, ?, ?, ?)", (event_id, buyer_email, quantity, price, coupon))
        conn.execute("COMMIT")
        return cur.lastrowid
    except BaseException:
        conn.execute("ROLLBACK")
        raise


def sales_report(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        """
        SELECT e.name AS event,
               COALESCE(SUM(o.quantity), 0) AS tickets_sold,
               COALESCE(SUM(o.quantity * o.unit_price_cents), 0) AS revenue_cents,
               e.capacity - COALESCE(SUM(o.quantity), 0) AS remaining
        FROM events e
        LEFT JOIN orders o ON o.event_id = e.id
        GROUP BY e.id
        ORDER BY e.name
        """
    ).fetchall()
    return [dict(r) for r in rows]
