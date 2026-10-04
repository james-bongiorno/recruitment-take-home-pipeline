# Challenge 2: bug hunt

**Time box: about 30 minutes.**

`invoices.py` builds invoices for event bookings: it turns prices into cents, adds up lines with tax and finds invoices in a date range. Someone wrote it quickly and **some of the tests fail**.

```bash
pip install pytest
pytest
```

## Your tasks

1. Fix the bugs in `invoices.py` so every test passes. **Don't change the existing tests.**
2. Add one new test of your own that would have caught one of the bugs sooner.
3. Write `NOTES.md` with a few lines for each bug: what was wrong, how you found it and how you fixed it.

Small, clear fixes beat rewrites. If you spot something that isn't a bug but you'd still change it, put it in NOTES.md rather than in the code.
