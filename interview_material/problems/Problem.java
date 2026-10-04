/*
 * Interview problem: library loans (Java)
 * Run it with:  java Problem.java      (Java 17+)
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
 *   c) Serve memberSummary as JSON from GET /members/{name}/summary (Spring Boot), or
 *      talk through how you would.
 *
 * The checks at the bottom print PASS or FAIL. Please don't change them.
 */
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

public class Problem {

    /** returnedDay 0 means not returned yet. */
    record Loan(String id, String member, String title, int dueDay, int returnedDay) {}

    record MemberRow(String member, int active, int overdue, int feesCents) {}

    static final int TODAY = 30;

    static final List<Loan> LOANS = List.of(
        new Loan("L1", "Ana", "Dune", 10, 12),
        new Loan("L2", "Ben", "Emma", 25, 0),
        new Loan("L3", "Ana", "Hamlet", 30, 0),
        new Loan("L4", "Cy", "Ulysses", 4, 0),
        new Loan("L5", "Ben", "Beloved", 20, 18)
    );

    static final int FEE_PER_DAY_CENTS = 25;
    static final int MAX_FEE_CENTS = 500;

    // ---------- Part 1: debug ----------

    /** How many days late the loan is (or was). Never negative. */
    static int daysLate(Loan loan, int today) {
        int end = loan.returnedDay() != 0 ? loan.returnedDay() : today;
        return end - loan.dueDay();
    }

    /** 25 cents per day late, capped at 500 cents. */
    static int lateFeeCents(int days) {
        return Math.max(days * FEE_PER_DAY_CENTS, MAX_FEE_CENTS);
    }

    /** True when the book hasn't come back and today is after the due day. */
    static boolean isOverdue(Loan loan, int today) {
        return loan.returnedDay() == 0 && today >= loan.dueDay();
    }

    // ---------- Part 2: implement ----------

    /**
     * One entry per member, sorted by name:
     *   [MemberRow[member=Ana, active=1, overdue=0, feesCents=50], ...]
     * active: loans not returned yet. overdue: loans that are overdue.
     * feesCents: late fees for all of the member's loans, returned or not.
     */
    static List<MemberRow> memberSummary(List<Loan> loans, int today) {
        // TODO
        return new ArrayList<>();
    }

    // ---------- Checks (don't change) ----------

    static void check(String name, Object actual, Object expected) {
        boolean ok = Objects.equals(actual, expected);
        System.out.println((ok ? "PASS" : "FAIL") + "  " + name);
        if (!ok) {
            System.out.println("      expected " + expected + "\n      got      " + actual);
        }
    }

    public static void main(String[] args) {
        check("daysLate, returned late", daysLate(LOANS.get(0), TODAY), 2);
        check("daysLate, returned early", daysLate(LOANS.get(4), TODAY), 0);
        check("lateFeeCents, capped", lateFeeCents(26), 500);
        check("lateFeeCents, on time", lateFeeCents(0), 0);
        check("isOverdue, due today", isOverdue(LOANS.get(2), TODAY), false);
        check("isOverdue, past due", isOverdue(LOANS.get(1), TODAY), true);
        check("memberSummary", memberSummary(LOANS, TODAY), List.of(
            new MemberRow("Ana", 1, 0, 50),
            new MemberRow("Ben", 1, 1, 125),
            new MemberRow("Cy", 1, 1, 500)
        ));
    }
}
