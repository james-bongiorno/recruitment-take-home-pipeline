# Coding challenges

Three sample take-homes for junior engineers. Each covers a different part of the stack and takes **about 75–100 minutes of work**. They share a made-up domain: a small venue that runs events.

| # | Folder | Part of the stack | Stack | Time |
|---|---|---|---|---|
| 1 | [`event-rsvp-take-home`](event-rsvp-take-home/) | Backend API, plus a debugging exercise | Python, FastAPI, pytest | ~100 min (two parts) |
| 2 | [`attendee-checkin`](attendee-checkin/) | Frontend UI, state and optimistic updates | React, TypeScript, Vitest | ~75 min |
| 3 | [`ticket-sales`](ticket-sales/) | Data layer and SQL | Python, SQLite, pytest | ~75 min |

The numbers are what you type into the **Create coding challenge** workflow. They're defined in [`challenges.json`](challenges.json).

Every challenge follows the same pattern:
- **Build** something from a short written spec.
- **Fix** a real-world bug. Across the three: money as floats, a mutable default argument, an off-by-one date range, a sort that mutates its input, `!=` against NULL, and integer division in SQL.
- **Write tests.**
- **Write a short `NOTES.md`.**

**These answer keys are public.** That's fine for trying the pipeline out, but before hiring for real, write your own challenges, or at least change these. See [Adding your own challenges](../README.md#adding-your-own-challenges).

## Layout of a challenge

```
<challenge>/
├── README.md              ← for you: what it is, what was checked
├── <candidate folder>/    ← exactly what the candidate receives (listed in challenges.json)
└── _reviewer_only/        ← rubric, reference solution, reviewer tests (never sent)
```

The pipeline copies only the folders listed in `challenges.json`. It also refuses to continue if a `_reviewer_only` or `solutions` folder turns up in what it's about to push.

## Reviewing

Each `_reviewer_only/RUBRIC.md` is scored out of 18. It includes the answer key and follow-up questions for the call afterwards. The reviewer tests only rely on behavior the README spells out, so they run against any candidate's structure.
