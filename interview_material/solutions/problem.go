/*
ANSWER KEY. Interview problem: library loans (Go)
Run it with:  go run problem.go      (Go 1.21+)

A small library lends books. Each loan has an id, the member's name, the book title,
the day it's due and the day it came back. Days are just numbers (day 1, day 2, ...),
and ReturnedDay 0 means the book hasn't come back yet. Today is day 30.

Rules:
  - Days late: from the due day to the day it came back (or to today if it hasn't come back).
    Returning early or on time is 0 days late, never negative.
  - Late fee: 25 cents per day late, but never more than 500 cents.
  - Overdue: the book hasn't come back AND today is after the due day.
    On the due day itself, it is not overdue yet.

PART 1: DEBUG (about 10 minutes)

	DaysLate, LateFeeCents and IsOverdue each have one bug.
	For each one: find it, explain what was wrong, then fix it.

PART 2: IMPLEMENT (about 15 minutes)

	Write MemberSummary. Its comment says what it returns.

PART 3: BONUS (if there's time; pick one)

	a) Renewals: write Renew(loan, today), which moves the due day 14 days later. Overdue
	   loans can't be renewed, and a loan can only be renewed twice.
	b) Some records arrive broken (no member, a negative or missing due day).
	   Skip them instead of crashing, and report how many were skipped.
	c) Serve MemberSummary as JSON from GET /members/{name}/summary (net/http), or talk
	   through how you would.

The checks at the bottom print PASS or FAIL. Please don't change them.
*/
package main

import (
	"fmt"
	"reflect"
	"sort"
)

// Loan is one borrowed book. ReturnedDay 0 means not returned yet.
type Loan struct {
	ID          string
	Member      string
	Title       string
	DueDay      int
	ReturnedDay int
}

type MemberRow struct {
	Member    string
	Active    int
	Overdue   int
	FeesCents int
}

const (
	Today          = 30
	FeePerDayCents = 25
	MaxFeeCents    = 500
)

var Loans = []Loan{
	{"L1", "Ana", "Dune", 10, 12},
	{"L2", "Ben", "Emma", 25, 0},
	{"L3", "Ana", "Hamlet", 30, 0},
	{"L4", "Cy", "Ulysses", 4, 0},
	{"L5", "Ben", "Beloved", 20, 18},
}

// ---------- Part 1: debug ----------

// DaysLate is how many days late the loan is (or was). Never negative.
func DaysLate(loan Loan, today int) int {
	end := today
	if loan.ReturnedDay != 0 {
		end = loan.ReturnedDay
	}
	return max(0, end-loan.DueDay)
}

// LateFeeCents is 25 cents per day late, capped at 500 cents.
func LateFeeCents(days int) int {
	return min(days*FeePerDayCents, MaxFeeCents)
}

// IsOverdue is true when the book hasn't come back and today is after the due day.
func IsOverdue(loan Loan, today int) bool {
	return loan.ReturnedDay == 0 && today > loan.DueDay
}

// ---------- Part 2: implement ----------

// MemberSummary returns one entry per member, sorted by name:
//
//	[]MemberRow{{Member: "Ana", Active: 1, Overdue: 0, FeesCents: 50}, ...}
//
// Active: loans not returned yet. Overdue: loans that are overdue.
// FeesCents: late fees for all of the member's loans, returned or not.
func MemberSummary(loans []Loan, today int) []MemberRow {
	index := map[string]int{} // member -> position in rows
	rows := []MemberRow{}
	for _, loan := range loans {
		i, seen := index[loan.Member]
		if !seen {
			i = len(rows)
			index[loan.Member] = i
			rows = append(rows, MemberRow{Member: loan.Member})
		}
		if loan.ReturnedDay == 0 {
			rows[i].Active++
		}
		if IsOverdue(loan, today) {
			rows[i].Overdue++
		}
		rows[i].FeesCents += LateFeeCents(DaysLate(loan, today))
	}
	sort.Slice(rows, func(a, b int) bool { return rows[a].Member < rows[b].Member })
	return rows
}

// ---------- Checks (don't change) ----------

func check(name string, actual, expected any) {
	ok := reflect.DeepEqual(actual, expected)
	status := "FAIL"
	if ok {
		status = "PASS"
	}
	fmt.Printf("%s  %s\n", status, name)
	if !ok {
		fmt.Printf("      expected %+v\n      got      %+v\n", expected, actual)
	}
}

func main() {
	check("DaysLate, returned late", DaysLate(Loans[0], Today), 2)
	check("DaysLate, returned early", DaysLate(Loans[4], Today), 0)
	check("LateFeeCents, capped", LateFeeCents(26), 500)
	check("LateFeeCents, on time", LateFeeCents(0), 0)
	check("IsOverdue, due today", IsOverdue(Loans[2], Today), false)
	check("IsOverdue, past due", IsOverdue(Loans[1], Today), true)
	check("MemberSummary", MemberSummary(Loans, Today), []MemberRow{
		{"Ana", 1, 0, 50},
		{"Ben", 1, 1, 125},
		{"Cy", 1, 1, 500},
	})
}
