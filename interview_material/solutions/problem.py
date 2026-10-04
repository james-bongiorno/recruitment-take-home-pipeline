"""
ANSWER KEY. Interview problem: library loans (Python)
Run it with:  python3 problem.py

A small library lends books. Each loan has an id, the member's name, the book title,
the day it's due and the day it came back. Days are just numbers (day 1, day 2, ...),
and returned_day 0 means the book hasn't come back yet. Today is day 30.

Rules:
  - Days late: from the due day to the day it came back (or to today if it hasn't come back).
    Returning early or on time is 0 days late, never negative.
  - Late fee: 25 cents per day late, but never more than 500 cents.
  - Overdue: the book hasn't come back AND today is after the due day.
    On the due day itself, it is not overdue yet.

PART 1: DEBUG (about 10 minutes)
  days_late, late_fee_cents and is_overdue each have one bug.
  For each one: find it, explain what was wrong, then fix it.

PART 2: IMPLEMENT (about 15 minutes)
  Write member_summary. Its docstring says what it returns.

PART 3: BONUS (if there's time; pick one)
  a) Renewals: write renew(loan, today), which moves the due day 14 days later. Overdue
     loans can't be renewed, and a loan can only be renewed twice.
  b) Some records arrive broken (no member, a negative or missing due day).
     Skip them instead of crashing, and report how many were skipped.
  c) Serve member_summary as JSON from GET /members/<name>/summary (Flask or FastAPI),
     or talk through how you would.

The checks at the bottom print PASS or FAIL. Please don't change them.
"""

TODAY = 30

LOANS = [
    {"id": "L1", "member": "Ana", "title": "Dune", "due_day": 10, "returned_day": 12},
    {"id": "L2", "member": "Ben", "title": "Emma", "due_day": 25, "returned_day": 0},
    {"id": "L3", "member": "Ana", "title": "Hamlet", "due_day": 30, "returned_day": 0},
    {"id": "L4", "member": "Cy", "title": "Ulysses", "due_day": 4, "returned_day": 0},
    {"id": "L5", "member": "Ben", "title": "Beloved", "due_day": 20, "returned_day": 18},
]

FEE_PER_DAY_CENTS = 25
MAX_FEE_CENTS = 500


# ---------- Part 1: debug ----------

def days_late(loan, today):
    """How many days late the loan is (or was). Never negative."""
    end = loan["returned_day"] if loan["returned_day"] else today
    return max(0, end - loan["due_day"])


def late_fee_cents(days):
    """25 cents per day late, capped at 500 cents."""
    return min(days * FEE_PER_DAY_CENTS, MAX_FEE_CENTS)


def is_overdue(loan, today):
    """True when the book hasn't come back and today is after the due day."""
    return loan["returned_day"] == 0 and today > loan["due_day"]


# ---------- Part 2: implement ----------

def member_summary(loans, today):
    """One entry per member, sorted by name:
        [{"member": "Ana", "active": 1, "overdue": 0, "fees_cents": 50}, ...]
    active: loans not returned yet. overdue: loans that are overdue.
    fees_cents: late fees for all of the member's loans, returned or not.
    """
    rows = {}
    for loan in loans:
        row = rows.setdefault(loan["member"], {"member": loan["member"], "active": 0, "overdue": 0, "fees_cents": 0})
        if loan["returned_day"] == 0:
            row["active"] += 1
        if is_overdue(loan, today):
            row["overdue"] += 1
        row["fees_cents"] += late_fee_cents(days_late(loan, today))
    return [rows[name] for name in sorted(rows)]


# ---------- Checks (don't change) ----------

def check(name, actual, expected):
    print(f"{'PASS' if actual == expected else 'FAIL'}  {name}")
    if actual != expected:
        print(f"      expected {expected!r}\n      got      {actual!r}")


if __name__ == "__main__":
    check("days_late, returned late", days_late(LOANS[0], TODAY), 2)
    check("days_late, returned early", days_late(LOANS[4], TODAY), 0)
    check("late_fee_cents, capped", late_fee_cents(26), 500)
    check("late_fee_cents, on time", late_fee_cents(0), 0)
    check("is_overdue, due today", is_overdue(LOANS[2], TODAY), False)
    check("is_overdue, past due", is_overdue(LOANS[1], TODAY), True)
    check("member_summary", member_summary(LOANS, TODAY), [
        {"member": "Ana", "active": 1, "overdue": 0, "fees_cents": 50},
        {"member": "Ben", "active": 1, "overdue": 1, "fees_cents": 125},
        {"member": "Cy", "active": 1, "overdue": 1, "fees_cents": 500},
    ])
