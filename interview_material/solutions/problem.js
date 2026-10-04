/*
 * ANSWER KEY. Interview problem: library loans (JavaScript)
 * Run it with:  node problem.js
 *
 * A small library lends books. Each loan has an id, the member's name, the book title,
 * the day it's due and the day it came back. Days are just numbers (day 1, day 2, ...),
 * and returnedDay 0 means the book hasn't come back yet. Today is day 30.
 *
 * Rules:
 *   - Days late: from the due day to the day it came back (or to today if it hasn't come back).
 *     Returning early or on time is 0 days late, never negative.
 *   - Late fee: 25 cents per day late, but never more than 500 cents.
 *   - Overdue: the book hasn't come back AND today is after the due day.
 *     On the due day itself, it is not overdue yet.
 *
 * PART 1: DEBUG (about 10 minutes)
 *   daysLate, lateFeeCents and isOverdue each have one bug.
 *   For each one: find it, explain what was wrong, then fix it.
 *
 * PART 2: IMPLEMENT (about 15 minutes)
 *   Write memberSummary. Its comment says what it returns.
 *
 * PART 3: BONUS (if there's time; pick one)
 *   a) Renewals: write renew(loan, today), which moves the due day 14 days later. Overdue
 *      loans can't be renewed, and a loan can only be renewed twice.
 *   b) Some records arrive broken (no member, a negative or missing due day).
 *      Skip them instead of crashing, and report how many were skipped.
 *   c) Serve memberSummary as JSON from GET /members/:name/summary (Express or plain
 *      node:http), or talk through how you would.
 *
 * The checks at the bottom print PASS or FAIL. Please don't change them.
 */

const TODAY = 30;

const LOANS = [
  { id: "L1", member: "Ana", title: "Dune", dueDay: 10, returnedDay: 12 },
  { id: "L2", member: "Ben", title: "Emma", dueDay: 25, returnedDay: 0 },
  { id: "L3", member: "Ana", title: "Hamlet", dueDay: 30, returnedDay: 0 },
  { id: "L4", member: "Cy", title: "Ulysses", dueDay: 4, returnedDay: 0 },
  { id: "L5", member: "Ben", title: "Beloved", dueDay: 20, returnedDay: 18 },
];

const FEE_PER_DAY_CENTS = 25;
const MAX_FEE_CENTS = 500;

// ---------- Part 1: debug ----------

/** How many days late the loan is (or was). Never negative. */
function daysLate(loan, today) {
  const end = loan.returnedDay ? loan.returnedDay : today;
  return Math.max(0, end - loan.dueDay);
}

/** 25 cents per day late, capped at 500 cents. */
function lateFeeCents(days) {
  return Math.min(days * FEE_PER_DAY_CENTS, MAX_FEE_CENTS);
}

/** True when the book hasn't come back and today is after the due day. */
function isOverdue(loan, today) {
  return loan.returnedDay === 0 && today > loan.dueDay;
}

// ---------- Part 2: implement ----------

/**
 * One entry per member, sorted by name:
 *   [{ member: "Ana", active: 1, overdue: 0, feesCents: 50 }, ...]
 * active: loans not returned yet. overdue: loans that are overdue.
 * feesCents: late fees for all of the member's loans, returned or not.
 */
function memberSummary(loans, today) {
  const rows = new Map();
  for (const loan of loans) {
    const row = rows.get(loan.member) ?? { member: loan.member, active: 0, overdue: 0, feesCents: 0 };
    if (loan.returnedDay === 0) row.active += 1;
    if (isOverdue(loan, today)) row.overdue += 1;
    row.feesCents += lateFeeCents(daysLate(loan, today));
    rows.set(loan.member, row);
  }
  return [...rows.values()].sort((a, b) => a.member.localeCompare(b.member));
}

// ---------- Checks (don't change) ----------

function check(name, actual, expected) {
  const ok = JSON.stringify(actual) === JSON.stringify(expected);
  console.log(`${ok ? "PASS" : "FAIL"}  ${name}`);
  if (!ok) {
    console.log(`      expected ${JSON.stringify(expected)}\n      got      ${JSON.stringify(actual)}`);
  }
}

check("daysLate, returned late", daysLate(LOANS[0], TODAY), 2);
check("daysLate, returned early", daysLate(LOANS[4], TODAY), 0);
check("lateFeeCents, capped", lateFeeCents(26), 500);
check("lateFeeCents, on time", lateFeeCents(0), 0);
check("isOverdue, due today", isOverdue(LOANS[2], TODAY), false);
check("isOverdue, past due", isOverdue(LOANS[1], TODAY), true);
check("memberSummary", memberSummary(LOANS, TODAY), [
  { member: "Ana", active: 1, overdue: 0, feesCents: 50 },
  { member: "Ben", active: 1, overdue: 1, feesCents: 125 },
  { member: "Cy", active: 1, overdue: 1, feesCents: 500 },
]);
