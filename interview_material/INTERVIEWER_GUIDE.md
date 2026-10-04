# Interviewer guide

**Format:** 45 minutes, shared screen, candidate's choice of language. Send them the one file at the start of the call and let them run it before they read any code.

| Time | Part |
|---|---|
| 0–5 | Intro. Have them run the file and tell you what they see. |
| 5–15 | Part 1: Debug |
| 15–30 | Part 2: Implement |
| 30–40 | Part 3: Bonus (pick the one that fits the role) |
| 40–45 | Their questions |

Ask them to talk while they work. How they find a bug matters more than how fast they fix it.

## Part 1: the three bugs (the same in every language)

| Function | Bug | Fix | Check that shows it |
|---|---|---|---|
| `daysLate` | Never clamps at zero, so a book returned 2 days early is "−2 days late" | `max(0, …)` | `daysLate, returned early` |
| `lateFeeCents` | Uses `max` where the cap needs `min`, so every fee is at least 500 and long ones aren't capped | `min(days × 25, 500)` | `lateFeeCents, capped` and `lateFeeCents, on time` |
| `isOverdue` | `>=` makes a book overdue on its due day | `>` | `isOverdue, due today` |

**What good looks like:** they read the failing output first, compare it with the rules in the header, form a guess and make a one-line fix. Ask them to explain each bug in one sentence. `max`/`min` for a cap is a classic. Candidates who say "`min` sets the ceiling" have a solid mental model.

**Hints, if they're stuck after about 3 minutes on one:**
- `daysLate`: "What should a book returned early count as?"
- `lateFeeCents`: "Which function picks the smaller of two numbers?"
- `isOverdue`: "Read the rule about the due day itself."

## Part 2: `memberSummary`

Expected output: Ana 1 active, 0 overdue, 50¢. Ben 1, 1, 125¢. Cy 1, 1, 500¢. Sorted by name.

It reuses all three Part 1 functions, so an unfixed bug shows up as wrong numbers here. That's a good moment to see whether they connect the two. Ben's 125¢ also depends on his early return counting as 0, not −50¢.

**What good looks like:** a map or dictionary keyed by member, a single pass, sorting at the end, and reusing `isOverdue` and the fee functions instead of copying the rules. The answer keys in `solutions/` show the idiomatic version for each language.

**Language-specific things worth noticing (not penalizing):**
- **JS/TS:** forgetting that `.sort()` with no comparer sorts by UTF-16 code unit. `localeCompare` is the careful choice.
- **Java:** `TreeMap` gives sorted keys for free.
- **Go:** map iteration order is random, so they must sort. Ask why. `min` and `max` are built in from Go 1.21.
- **PHP:** they need `array_values` after `ksort`, or the keys leak into the result and the check fails.
- **C#/Ruby:** LINQ `GroupBy` or Ruby's `group_by` are fine, and so is a manual loop.

## Part 3: bonus options

- **a) Renewals:** watch how they track the renewal count (a new field? a separate map?), and whether they refuse overdue loans *before* changing anything.
- **b) Broken records:** validate up front, then skip and count. Watch for a try/catch around everything that hides real bugs.
- **c) API endpoint:** look for status codes (404 for an unknown member, or an empty summary?), JSON content type, and where validation lives. Writing the code is optional; a clear walkthrough counts.

## Scoring (0–2 each, 10 total)

| Area | 0 | 1 | 2 |
|---|---|---|---|
| **Debugging process** | Guessed at random or rewrote functions | Found the bugs with heavy hints | Read the output, compared it with the rules, made minimal fixes |
| **Explaining** | Couldn't say what was wrong | Described the fix but not the cause | Clear one-line cause for each bug |
| **Implementation** | Didn't work | Worked with help, or copied rules instead of reusing functions | Clean single pass, sorted, reused the Part 1 functions |
| **Language fluency** | Fought the syntax throughout | Some lookups, got there | Idiomatic for the language they chose |
| **Bonus / curiosity** | Didn't get there | Attempted it | Asked good clarifying questions, sensible design |

Rough read: **8–10** is strong, **5–7** is promising for a junior, **under 5** is not yet.
