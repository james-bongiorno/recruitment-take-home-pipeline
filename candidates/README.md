# Candidates

Written by the hiring pipeline. You normally don't edit anything here by hand.

```
candidates/
├── under-review/<last>_<first>/   ← created by "Create coding challenge", updated hourly by "Sync submissions"
└── reviewed/<last>_<first>/       ← moved here by "Close out candidate"
```

Each candidate folder holds:

| File | What it is |
|---|---|
| `candidate.json` | Name, challenges, GitHub usernames, repo link, created time, deadline, status (`active` → `deadline_passed` → `closed`) |
| `activity.log` | Everything that happened, in time order: invitations accepted, PRs opened / closed / reopened, commits, force-pushes, anything landing on `main`, the deadline, close-out. Anything after the deadline is marked `[after deadline]`. |
| `submission/` | A copy of their latest PR's files, refreshed whenever they push. `.github/`, `node_modules/`, symlinks and files over 2 MB are left out. |
| `submission.patch` | Only their changes compared with the starter. Usually the quickest thing to read first. |
| `sync_state.json` | Bookkeeping for the sync so it never logs the same event twice. |

**Reading the log:** PR events, force-pushes and accepted invitations come from GitHub's own records, so a candidate can't edit them. Commit times come from the commits themselves, which a candidate can set to anything, so treat those as approximate. "Accepted the invitation" is stamped with the time the sync noticed it, not the exact time.

**Never run code from `submission/` on your machine without looking at it first,** and never from a workflow in this repo. It's untrusted code.
