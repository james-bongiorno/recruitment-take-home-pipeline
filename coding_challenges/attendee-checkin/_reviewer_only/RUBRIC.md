# Reviewer rubric: Door check-in list

Score each row 0–2. A strong junior lands around 12+ of 18. Spend most of the follow-up call on their own walkthrough.

| Area | 0 | 1 | 2 |
|---|---|---|---|
| **Sort bug** | Not fixed, or the test was changed | Fixed, but not explained | Fixed with a copy or `toSorted()`, and they explain mutating state or props in React |
| **Loading, error and empty states** | Missing | Some, or retry doesn't work | All three, and retry loads again |
| **List and search** | Missing or wrong | Mostly right | Sorted, VIP shown, case-insensitive search on name and email, "no match" message, the count covers everyone |
| **Optimistic update** | Waits for the server, or no rollback | Updates right away, but rollback is buggy | Updates right away, rolls back only that attendee, clear error, uses functional state updates |
| **Tests** | None added | The 3 asked for | Meaningful extras (undo, optimistic before the server answers, nobody matching) |
| **Code clarity** | Hard to follow | Readable | Clear state, derived values computed rather than stored, no dead code |
| **TypeScript** | `any` everywhere, or the typecheck fails | Passes with loose types | Clean types, no casts |
| **Notes** | Missing | Lists what they did | Honest time spent, trade-offs, next steps, AI use disclosed |
| **Git / hygiene** | `node_modules` committed | Clean | Sensible commits, PR description explains the work |

## Answer key

- `src/lib/attendees.ts` and `src/components/CheckInList.tsx` in this folder are one reasonable answer.
- Copy `src/components/CheckInList.reviewer.test.tsx` into their `src/components/` and run `npm test`. The reference passes all 14 tests, and the untouched starter fails 11.
- **The sort bug:** `attendees.sort(...)` sorts in place and returns the same array. Called on React state during render, it quietly reorders state without `setState`, which can make the UI disagree with the data later. Fixes: `[...attendees].sort(...)`, `attendees.slice().sort(...)` or `attendees.toSorted(...)`.

## Follow-up call questions

- Why update the screen before the server answers? When would you *not* do that?
- Walk me through what happens if two check-ins are in flight and the first one fails. (Look for functional `setState` and thinking about which value to roll back to.)
- Where would you put this logic in a bigger app (a custom hook, React Query mutations)?
- How would this work offline, for example queuing check-ins until the Wi-Fi comes back?
