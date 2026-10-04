# Take-home: Door check-in list (frontend)

A React and TypeScript list that door staff use to check people in, with search and optimistic updates that roll back when saving fails. It also has a real bug to fix: `Array.prototype.sort` changes the array it's called on. **About 75 minutes.**

- **Send:** the pipeline sends `checkin/` (challenge 2 in `challenges.json`). By hand, zip `checkin/` without `node_modules`.
- **Review:** `_reviewer_only/RUBRIC.md`. Copy `_reviewer_only/src/` over a copy of their project, or just drop in the reviewer test file.
- **Checked:** the starter fails 2 of its 5 tests. The reference passes all 14 (including the reviewer tests) and `npm run typecheck`.
