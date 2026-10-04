import pytest

from sales.db import add_event, connect


@pytest.fixture
def conn():
    """A fresh in-memory database for each test."""
    c = connect()
    yield c
    c.close()


@pytest.fixture
def jazz(conn):
    """An event with 10 seats at $25.00."""
    return add_event(conn, "Jazz Night", 10, 2500)


def insert_order(conn, event_id, quantity, coupon=None, email="fan@example.com", unit_price_cents=2500):
    """Insert an order directly, without place_order(), for setting up tests."""
    with conn:
        return conn.execute(
            "INSERT INTO orders (event_id, buyer_email, quantity, unit_price_cents, coupon)"
            " VALUES (?, ?, ?, ?, ?)", (event_id, email, quantity, unit_price_cents, coupon)
        ).lastrowid
