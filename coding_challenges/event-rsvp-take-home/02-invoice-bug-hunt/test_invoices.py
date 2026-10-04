from invoices import add_line, invoices_between, new_invoice, to_cents, total_cents


def test_to_cents_whole_dollars():
    assert to_cents("5") == 500


def test_to_cents_with_cents():
    assert to_cents("19.99") == 1999


def test_to_cents_small_amount():
    assert to_cents("0.29") == 29


def test_total_includes_tax():
    inv = new_invoice("Ada")
    add_line(inv, "Jazz Night ticket", "25.00", 2)
    assert total_cents(inv) == 5400  # 5000 + 400 tax


def test_invoices_start_empty():
    first = new_invoice("Ada")
    add_line(first, "Jazz Night ticket", "25.00")
    second = new_invoice("Grace")
    assert second["lines"] == []


def test_invoices_between_includes_both_ends():
    invoices = [{"id": 1, "date": "2026-03-01"}, {"id": 2, "date": "2026-03-15"},
                {"id": 3, "date": "2026-03-31"}, {"id": 4, "date": "2026-04-01"}]
    assert [i["id"] for i in invoices_between(invoices, "2026-03-01", "2026-03-31")] == [1, 2, 3]
