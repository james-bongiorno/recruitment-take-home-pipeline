# Interview problem: library loans (Ruby)
# Run it with:  ruby problem.rb
#
# A small library lends books. Each loan has an id, the member's name, the book title,
# the day it's due and the day it came back. Days are just numbers (day 1, day 2, ...),
# and returned_day 0 means the book hasn't come back yet. Today is day 30.
#
# Rules:
#   - Days late: from the due day to the day it came back (or to today if it hasn't come back).
#     Returning early or on time is 0 days late, never negative.
#   - Late fee: 25 cents per day late, but never more than 500 cents.
#   - Overdue: the book hasn't come back AND today is after the due day.
#     On the due day itself, it is not overdue yet.
#
# PART 1: DEBUG (about 10 minutes)
#   days_late, late_fee_cents and overdue? each have one bug.
#   For each one: find it, explain what was wrong, then fix it.
#
# PART 2: IMPLEMENT (about 15 minutes)
#   Write member_summary. Its comment says what it returns.
#
# PART 3: BONUS (if there's time; pick one)
#   a) Renewals: write renew(loan, today), which moves the due day 14 days later. Overdue
#      loans can't be renewed, and a loan can only be renewed twice.
#   b) Some records arrive broken (no member, a negative or missing due day).
#      Skip them instead of crashing, and report how many were skipped.
#   c) Serve member_summary as JSON from GET /members/:name/summary (Sinatra or Rails),
#      or talk through how you would.
#
# The checks at the bottom print PASS or FAIL. Please don't change them.

TODAY = 30

LOANS = [
  { id: "L1", member: "Ana", title: "Dune", due_day: 10, returned_day: 12 },
  { id: "L2", member: "Ben", title: "Emma", due_day: 25, returned_day: 0 },
  { id: "L3", member: "Ana", title: "Hamlet", due_day: 30, returned_day: 0 },
  { id: "L4", member: "Cy", title: "Ulysses", due_day: 4, returned_day: 0 },
  { id: "L5", member: "Ben", title: "Beloved", due_day: 20, returned_day: 18 }
].freeze

FEE_PER_DAY_CENTS = 25
MAX_FEE_CENTS = 500

# ---------- Part 1: debug ----------

# How many days late the loan is (or was). Never negative.
def days_late(loan, today)
  finish = loan[:returned_day].zero? ? today : loan[:returned_day]
  finish - loan[:due_day]
end

# 25 cents per day late, capped at 500 cents.
def late_fee_cents(days)
  [days * FEE_PER_DAY_CENTS, MAX_FEE_CENTS].max
end

# True when the book hasn't come back and today is after the due day.
def overdue?(loan, today)
  loan[:returned_day].zero? && today >= loan[:due_day]
end

# ---------- Part 2: implement ----------

# One entry per member, sorted by name:
#   [{ member: "Ana", active: 1, overdue: 0, fees_cents: 50 }, ...]
# active: loans not returned yet. overdue: loans that are overdue.
# fees_cents: late fees for all of the member's loans, returned or not.
def member_summary(loans, today)
  # TODO
  []
end

# ---------- Checks (don't change) ----------

def check(name, actual, expected)
  ok = actual == expected
  puts "#{ok ? 'PASS' : 'FAIL'}  #{name}"
  puts "      expected #{expected.inspect}\n      got      #{actual.inspect}" unless ok
end

check("days_late, returned late", days_late(LOANS[0], TODAY), 2)
check("days_late, returned early", days_late(LOANS[4], TODAY), 0)
check("late_fee_cents, capped", late_fee_cents(26), 500)
check("late_fee_cents, on time", late_fee_cents(0), 0)
check("overdue?, due today", overdue?(LOANS[2], TODAY), false)
check("overdue?, past due", overdue?(LOANS[1], TODAY), true)
check("member_summary", member_summary(LOANS, TODAY), [
  { member: "Ana", active: 1, overdue: 0, fees_cents: 50 },
  { member: "Ben", active: 1, overdue: 1, fees_cents: 125 },
  { member: "Cy", active: 1, overdue: 1, fees_cents: 500 }
])
