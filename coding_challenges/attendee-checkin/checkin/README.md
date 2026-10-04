# Challenge: Door check-in list (frontend)

**Time box: about 75 minutes of work** (you have 48 hours to send it back). Please stop at about 90 minutes even if you're not finished, and tell us what you'd do next. We care more about clear, working code than about finishing everything.

## The situation

At the door of an event, staff check people in on a tablet. The Wi-Fi is often bad, so the screen has to feel instant: a tap should show the change right away, and if the server refuses, the screen has to put things back and say so.

Your job is to build that list in React and TypeScript, and fix a bug a teammate found along the way.

## What's already here

```
src/types.ts                      Attendee and AttendeesApi types
src/api.ts                        A fake API with three events (no backend needed)
src/lib/attendees.ts              Sorting, search and counting helpers (one bug, see task 1)
src/components/CheckInList.tsx    The component you'll build
src/App.tsx                       A page with an event picker, already wired to the fake API
```

Setup (Node 20+):

```bash
npm install
npm test          # 2 tests fail until you do tasks 1 and 2
npm run dev       # then open the URL it prints
```

## Your tasks

1. **Fix `sortAttendees`.** A teammate noticed that after the list is sorted, the original data they passed in has changed order too. The failing test shows it. Fix it, and explain in NOTES.md why this matters in a React app.

2. **Build `CheckInList`** in `src/components/CheckInList.tsx`. It gets an `eventId` and an `api`, and:
   - Loads the attendees with `api.list(eventId)`.
   - **While loading**, shows `Loading attendees…`
   - **If loading fails**, shows `Couldn't load attendees.` and a `Try again` button that loads again.
   - **If there are no attendees**, shows `No attendees yet.`
   - **Otherwise**, shows:
     - `X of Y checked in`, counting everyone, not only the people the search is showing
     - A search box labelled `Search attendees` that filters by name or email, ignoring case. If nothing matches, show `No attendees match "<query>".`
     - A list (`<ul>`) with one item per attendee, sorted by name using `sortAttendees`. Each item shows the name, the email, `VIP` for VIP tickets, and a button: `Check in`, or `Undo check-in` if they're already checked in.
   - **Checking in** (or undoing it) updates the screen **immediately**, then calls `api.setCheckedIn(id, checkedIn)`. If that fails, put the attendee back the way they were and show `Couldn't update <name>. Try again.`

   Please use the exact text above, since our own tests look for it. How you structure the code is up to you.

3. **Tests.** Add tests to `src/components/CheckInList.test.tsx` for at least: the error message and retry, search, and a check-in that fails and rolls back.

4. **`NOTES.md`** (5–10 lines): the cause of the sorting bug, decisions you made, anything you'd change with more time, and roughly how long you spent.

## Ground rules

- No new libraries unless you explain why in NOTES.md. Plain React is fine. Styling isn't judged.
- Documentation and search are fine. If you use an AI assistant, say where in NOTES.md. We'll ask you to walk through your code either way.
- Send it back as a zip (without `node_modules`) or a link to a private GitHub repo. Please don't post it publicly.

## Optional, only if you have time left

A staff member taps the same person's button twice quickly, and the first save fails after the second one has started. What should the screen show? Make it behave sensibly, or explain in NOTES.md how you would.
