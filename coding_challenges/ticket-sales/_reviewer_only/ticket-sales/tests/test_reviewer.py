"""Extra checks (reviewer only). Drop into the candidate's tests/ folder and run pytest."""
import sqlite3

import pytest

from sales.db import SoldOut, add_event, place_order, sales_report
from tests.conftest import insert_order


@pytest.mark.parametrize("quantity", [0, 11, -1])
def test_quantity_limits_in_the_database(conn, jazz, quantity):
    with pytest.raises(sqlite3.IntegrityError):
        insert_order(conn, jazz, quantity)


@pytest.mark.parametrize("email", [None, "", "not-an-email", "@example.com"])
def test_email_checked_in_the_database(conn, jazz, email):
    with pytest.raises(sqlite3.IntegrityError):
        insert_order(conn, jazz, 1, email=email)


def test_order_needs_a_real_event(conn):
    with pytest.raises(sqlite3.IntegrityError):
        insert_order(conn, 999, 1)


def test_event_is_required(conn):
    with pytest.raises(sqlite3.IntegrityError):
        insert_order(conn, None, 1)


def test_price_cannot_be_negative(conn, jazz):
    with pytest.raises(sqlite3.IntegrityError):
        insert_order(conn, jazz, 1, unit_price_cents=-5)


def test_cannot_delete_an_event_with_sales(conn, jazz):
    insert_order(conn, jazz, 1)
    with pytest.raises(sqlite3.IntegrityError):
        with conn:
            conn.execute("DELETE FROM events WHERE id = ?", (jazz,))


def test_order_copies_the_price_and_comp_is_free(conn, jazz):
    paid = place_order(conn, jazz, "a@example.com", 2)
    free = place_order(conn, jazz, "b@example.com", 1, coupon="COMP")
    tracked = place_order(conn, jazz, "c@example.com", 1, coupon="RADIO")
    prices = dict(conn.execute("SELECT id, unit_price_cents FROM orders").fetchall())
    assert prices == {paid: 2500, free: 0, tracked: 2500}


def test_selling_exactly_the_last_tickets_works(conn, jazz):
    place_order(conn, jazz, "a@example.com", 7)
    place_order(conn, jazz, "b@example.com", 3)
    with pytest.raises(SoldOut):
        place_order(conn, jazz, "c@example.com", 1)


def test_sold_out_order_is_not_saved(conn, jazz):
    place_order(conn, jazz, "a@example.com", 9)
    with pytest.raises(SoldOut):
        place_order(conn, jazz, "b@example.com", 2)
    assert conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 1


def test_unknown_event(conn):
    with pytest.raises(LookupError):
        place_order(conn, 999, "a@example.com", 1)


def test_orders_are_saved_to_a_file(tmp_path):
    from sales.db import connect
    path = str(tmp_path / "sales.db")
    c = connect(path)
    event = add_event(c, "Jazz Night", 10, 2500)
    place_order(c, event, "a@example.com", 2)
    c.close()
    assert sales_report(connect(path))[0]["tickets_sold"] == 2


def test_sales_report(conn, jazz):
    add_event(conn, "Art Walk", 50, 0)  # no orders: still listed
    pottery = add_event(conn, "Pottery 101", 6, 4000)
    place_order(conn, jazz, "a@example.com", 2)
    place_order(conn, jazz, "b@example.com", 1, coupon="COMP")
    place_order(conn, pottery, "c@example.com", 6)
    assert sales_report(conn) == [
        {"event": "Art Walk", "tickets_sold": 0, "revenue_cents": 0, "remaining": 50},
        {"event": "Jazz Night", "tickets_sold": 3, "revenue_cents": 5000, "remaining": 7},
        {"event": "Pottery 101", "tickets_sold": 6, "revenue_cents": 24000, "remaining": 0},
    ]


def test_sales_report_empty(conn):
    assert sales_report(conn) == []
