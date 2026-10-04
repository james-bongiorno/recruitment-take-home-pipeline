/*
 * Interview problem: library loans (C#)
 * Run it with:  dotnet run Problem.cs                       (.NET 10+)
 *   On .NET 8 or 9:  dotnet new console -o problem, replace problem/Program.cs
 *                    with this file, then run  dotnet run --project problem
 *
 * A small library lends books. Each loan has an id, the member's name, the book title,
 * the day it's due and the day it came back. Days are just numbers (day 1, day 2, ...),
 * and ReturnedDay 0 means the book hasn't come back yet. Today is day 30.
 *
 * Rules:
 *   - Days late: from the due day to the day it came back (or to today if it hasn't come back).
 *     Returning early or on time is 0 days late, never negative.
 *   - Late fee: 25 cents per day late, but never more than 500 cents.
 *   - Overdue: the book hasn't come back AND today is after the due day.
 *     On the due day itself, it is not overdue yet.
 *
 * PART 1: DEBUG (about 10 minutes)
 *   DaysLate, LateFeeCents and IsOverdue each have one bug.
 *   For each one: find it, explain what was wrong, then fix it.
 *
 * PART 2: IMPLEMENT (about 15 minutes)
 *   Write MemberSummary. Its comment says what it returns.
 *
 * PART 3: BONUS (if there's time; pick one)
 *   a) Renewals: write Renew(loan, today), which moves the due day 14 days later. Overdue
 *      loans can't be renewed, and a loan can only be renewed twice.
 *   b) Some records arrive broken (no member, a negative or missing due day).
 *      Skip them instead of crashing, and report how many were skipped.
 *   c) Serve MemberSummary as JSON from GET /members/{name}/summary (ASP.NET Core
 *      minimal API), or talk through how you would.
 *
 * The checks at the bottom print PASS or FAIL. Please don't change them.
 */
using System;
using System.Collections.Generic;
using System.Linq;

/// <summary>ReturnedDay 0 means not returned yet.</summary>
public record Loan(string Id, string Member, string Title, int DueDay, int ReturnedDay);

public record MemberRow(string Member, int Active, int Overdue, int FeesCents);

public static class Problem
{
    const int Today = 30;
    const int FeePerDayCents = 25;
    const int MaxFeeCents = 500;

    static readonly List<Loan> Loans = new()
    {
        new("L1", "Ana", "Dune", 10, 12),
        new("L2", "Ben", "Emma", 25, 0),
        new("L3", "Ana", "Hamlet", 30, 0),
        new("L4", "Cy", "Ulysses", 4, 0),
        new("L5", "Ben", "Beloved", 20, 18),
    };

    // ---------- Part 1: debug ----------

    /// <summary>How many days late the loan is (or was). Never negative.</summary>
    static int DaysLate(Loan loan, int today)
    {
        int end = loan.ReturnedDay != 0 ? loan.ReturnedDay : today;
        return end - loan.DueDay;
    }

    /// <summary>25 cents per day late, capped at 500 cents.</summary>
    static int LateFeeCents(int days)
    {
        return Math.Max(days * FeePerDayCents, MaxFeeCents);
    }

    /// <summary>True when the book hasn't come back and today is after the due day.</summary>
    static bool IsOverdue(Loan loan, int today)
    {
        return loan.ReturnedDay == 0 && today >= loan.DueDay;
    }

    // ---------- Part 2: implement ----------

    /// <summary>
    /// One entry per member, sorted by name:
    ///   [MemberRow { Member = Ana, Active = 1, Overdue = 0, FeesCents = 50 }, ...]
    /// Active: loans not returned yet. Overdue: loans that are overdue.
    /// FeesCents: late fees for all of the member's loans, returned or not.
    /// </summary>
    static List<MemberRow> MemberSummary(List<Loan> loans, int today)
    {
        // TODO
        return new List<MemberRow>();
    }

    // ---------- Checks (don't change) ----------

    static void Check(string name, object? actual, object? expected)
    {
        bool ok = actual is IEnumerable<MemberRow> a && expected is IEnumerable<MemberRow> e
            ? a.SequenceEqual(e)
            : Equals(actual, expected);
        Console.WriteLine($"{(ok ? "PASS" : "FAIL")}  {name}");
        if (!ok)
        {
            Console.WriteLine($"      expected {Show(expected)}\n      got      {Show(actual)}");
        }
    }

    static string Show(object? value) => value is IEnumerable<MemberRow> rows
        ? "[" + string.Join(", ", rows) + "]"
        : value?.ToString() ?? "null";

    public static void Main()
    {
        Check("DaysLate, returned late", DaysLate(Loans[0], Today), 2);
        Check("DaysLate, returned early", DaysLate(Loans[4], Today), 0);
        Check("LateFeeCents, capped", LateFeeCents(26), 500);
        Check("LateFeeCents, on time", LateFeeCents(0), 0);
        Check("IsOverdue, due today", IsOverdue(Loans[2], Today), false);
        Check("IsOverdue, past due", IsOverdue(Loans[1], Today), true);
        Check("MemberSummary", MemberSummary(Loans, Today), new List<MemberRow>
        {
            new("Ana", 1, 0, 50),
            new("Ben", 1, 1, 125),
            new("Cy", 1, 1, 500),
        });
    }
}
