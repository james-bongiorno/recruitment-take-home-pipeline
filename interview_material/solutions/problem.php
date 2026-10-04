<?php
/*
 * ANSWER KEY. Interview problem: library loans (PHP)
 * Run it with:  php problem.php      (PHP 8+)
 *
 * A small library lends books. Each loan has an id, the member's name, the book title,
 * the day it's due and the day it came back. Days are just numbers (day 1, day 2, ...),
 * and returned_day 0 means the book hasn't come back yet. Today is day 30.
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
 *   a) Renewals: write renew($loan, $today), which moves the due day 14 days later. Overdue
 *      loans can't be renewed, and a loan can only be renewed twice.
 *   b) Some records arrive broken (no member, a negative or missing due day).
 *      Skip them instead of crashing, and report how many were skipped.
 *   c) Serve memberSummary as JSON from GET /members/{name}/summary (Laravel, Slim or a
 *      plain PHP file), or talk through how you would.
 *
 * The checks at the bottom print PASS or FAIL. Please don't change them.
 */

const TODAY = 30;

const LOANS = [
    ['id' => 'L1', 'member' => 'Ana', 'title' => 'Dune', 'due_day' => 10, 'returned_day' => 12],
    ['id' => 'L2', 'member' => 'Ben', 'title' => 'Emma', 'due_day' => 25, 'returned_day' => 0],
    ['id' => 'L3', 'member' => 'Ana', 'title' => 'Hamlet', 'due_day' => 30, 'returned_day' => 0],
    ['id' => 'L4', 'member' => 'Cy', 'title' => 'Ulysses', 'due_day' => 4, 'returned_day' => 0],
    ['id' => 'L5', 'member' => 'Ben', 'title' => 'Beloved', 'due_day' => 20, 'returned_day' => 18],
];

const FEE_PER_DAY_CENTS = 25;
const MAX_FEE_CENTS = 500;

// ---------- Part 1: debug ----------

/** How many days late the loan is (or was). Never negative. */
function daysLate(array $loan, int $today): int
{
    $end = $loan['returned_day'] ?: $today;
    return max(0, $end - $loan['due_day']);
}

/** 25 cents per day late, capped at 500 cents. */
function lateFeeCents(int $days): int
{
    return min($days * FEE_PER_DAY_CENTS, MAX_FEE_CENTS);
}

/** True when the book hasn't come back and today is after the due day. */
function isOverdue(array $loan, int $today): bool
{
    return $loan['returned_day'] === 0 && $today > $loan['due_day'];
}

// ---------- Part 2: implement ----------

/**
 * One entry per member, sorted by name:
 *   [['member' => 'Ana', 'active' => 1, 'overdue' => 0, 'fees_cents' => 50], ...]
 * active: loans not returned yet. overdue: loans that are overdue.
 * fees_cents: late fees for all of the member's loans, returned or not.
 */
function memberSummary(array $loans, int $today): array
{
    $rows = [];
    foreach ($loans as $loan) {
        $m = $loan['member'];
        $rows[$m] ??= ['member' => $m, 'active' => 0, 'overdue' => 0, 'fees_cents' => 0];
        if ($loan['returned_day'] === 0) {
            $rows[$m]['active']++;
        }
        if (isOverdue($loan, $today)) {
            $rows[$m]['overdue']++;
        }
        $rows[$m]['fees_cents'] += lateFeeCents(daysLate($loan, $today));
    }
    ksort($rows);
    return array_values($rows);
}

// ---------- Checks (don't change) ----------

function check(string $name, mixed $actual, mixed $expected): void
{
    $ok = $actual === $expected;
    echo ($ok ? 'PASS' : 'FAIL') . "  $name\n";
    if (!$ok) {
        echo '      expected ' . json_encode($expected) . "\n      got      " . json_encode($actual) . "\n";
    }
}

check('daysLate, returned late', daysLate(LOANS[0], TODAY), 2);
check('daysLate, returned early', daysLate(LOANS[4], TODAY), 0);
check('lateFeeCents, capped', lateFeeCents(26), 500);
check('lateFeeCents, on time', lateFeeCents(0), 0);
check('isOverdue, due today', isOverdue(LOANS[2], TODAY), false);
check('isOverdue, past due', isOverdue(LOANS[1], TODAY), true);
check('memberSummary', memberSummary(LOANS, TODAY), [
    ['member' => 'Ana', 'active' => 1, 'overdue' => 0, 'fees_cents' => 50],
    ['member' => 'Ben', 'active' => 1, 'overdue' => 1, 'fees_cents' => 125],
    ['member' => 'Cy', 'active' => 1, 'overdue' => 1, 'fees_cents' => 500],
]);
