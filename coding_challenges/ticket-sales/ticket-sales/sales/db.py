"""Data layer for events and ticket orders, on SQLite."""
import sqlite3
from pathlib import Path

SCHEMA = Path(__file__).with_name("schema.sql")
COMP = "COMP"  # coupon for complimentary (free) tickets


class SoldOut(Exception):
    """Not enough tickets left for this order."""


def connect(path: str = ":memory:") -> sqlite3.Connection:
    """Open a database, create the tables if needed, and return the connection."""
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA.read_text())
    return conn


def add_event(conn: sqlite3.Connection, name: str, capacity: int, price_cents: int) -> int:
    with conn:
        cur = conn.execute("INSERT INTO events (name, capacity, price_cents) VALUES (?, ?, ?)",
                           (name, capacity, price_cents))
    return cur.lastrowid


def average_order_size(conn: sqlite3.Connection, event_id: int) -> float | None:
    """Average tickets per order for an event, e.g. 2.5. None if it has no orders."""
    row = conn.execute(
        "SELECT SUM(quantity) / COUNT(*) AS avg FROM orders WHERE event_id = ?", (event_id,)
    ).fetchone()
    return row["avg"]


def paid_orders(conn: sqlite3.Connection, event_id: int) -> list[dict]:
    """Every order for the event except complimentary ones (coupon COMP), oldest first.
    Orders with no coupon at all are paid orders."""
    rows = conn.execute(
        "SELECT * FROM orders WHERE event_id = ? AND coupon != ? ORDER BY id", (event_id, COMP)
    ).fetchall()
    return [dict(r) for r in rows]


def place_order(conn: sqlite3.Connection, event_id: int, buyer_email: str, quantity: int,
                coupon: str | None = None) -> int:
    """Sell tickets and return the order id. See README.md for the rules."""
    # TODO (task 3)
    raise NotImplementedError


def sales_report(conn: sqlite3.Connection) -> list[dict]:
    """One row per event, sorted by name:
    {"event": name, "tickets_sold": int, "revenue_cents": int, "remaining": int}"""
    # TODO (task 3)
    raise NotImplementedError
