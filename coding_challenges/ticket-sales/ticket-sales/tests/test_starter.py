import pytest

from sales.db import SoldOut, average_order_size, paid_orders, place_order
from tests.conftest import insert_order


def test_average_order_size(conn, jazz):
    insert_order(conn, jazz, 2)
    insert_order(conn, jazz, 3)
    assert average_order_size(conn, jazz) == pytest.approx(2.5)


def test_average_order_size_with_no_orders(conn, jazz):
    assert average_order_size(conn, jazz) is None


def test_paid_orders_leave_out_comps_only(conn, jazz):
    paid = insert_order(conn, jazz, 2)                    # no coupon
    tracked = insert_order(conn, jazz, 1, coupon="RADIO")  # a tracking code, still paid
    insert_order(conn, jazz, 2, coupon="COMP")
    assert [o["id"] for o in paid_orders(conn, jazz)] == [paid, tracked]


def test_cannot_oversell(conn, jazz):
    place_order(conn, jazz, "a@example.com", 8)
    with pytest.raises(SoldOut):
        place_order(conn, jazz, "b@example.com", 3)


# TODO: add your tests here (see README.md, task 4)
