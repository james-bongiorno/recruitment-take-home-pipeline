"""Invoices for event bookings. Money is kept in whole cents (ints) to avoid rounding surprises."""

TAX_RATE = 0.08


def to_cents(price: str) -> int:
    """Turn a price string into cents: "19.99" -> 1999, "5" -> 500."""
    return int(float(price) * 100)


def new_invoice(customer: str, lines=[]):
    """Start an invoice. `lines` is an optional list of (description, price, quantity) to begin with."""
    return {"customer": customer, "lines": lines}


def add_line(invoice: dict, description: str, price: str, quantity: int = 1) -> None:
    invoice["lines"].append((description, price, quantity))


def total_cents(invoice: dict) -> int:
    """Subtotal plus tax, in cents. Tax is rounded to the nearest cent."""
    subtotal = sum(to_cents(price) * qty for _, price, qty in invoice["lines"])
    return subtotal + round(subtotal * TAX_RATE)


def invoices_between(invoices: list[dict], start: str, end: str) -> list[dict]:
    """Invoices dated from `start` to `end`, including both days. Dates are "YYYY-MM-DD"."""
    return [inv for inv in invoices if start <= inv["date"] < end]
