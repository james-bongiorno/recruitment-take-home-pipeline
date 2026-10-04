"""Reference fix (reviewer only).

Bugs:
  1. to_cents: float("19.99") * 100 is 1998.9999..., and int() truncates it to 1998.
     Fix: round() instead of int(), or better, Decimal(price) * 100.
  2. new_invoice: `lines=[]` is created once when the function is defined, so every invoice
     made without lines shares the same list. Fix: default to None and make a new list.
  3. invoices_between: `< end` leaves out invoices dated on the end day. Fix: `<= end`.
"""
from decimal import Decimal

TAX_RATE = 0.08


def to_cents(price: str) -> int:
    return int(Decimal(price) * 100)


def new_invoice(customer: str, lines=None):
    return {"customer": customer, "lines": list(lines) if lines else []}


def add_line(invoice: dict, description: str, price: str, quantity: int = 1) -> None:
    invoice["lines"].append((description, price, quantity))


def total_cents(invoice: dict) -> int:
    subtotal = sum(to_cents(price) * qty for _, price, qty in invoice["lines"])
    return subtotal + round(subtotal * TAX_RATE)


def invoices_between(invoices: list[dict], start: str, end: str) -> list[dict]:
    return [inv for inv in invoices if start <= inv["date"] <= end]
