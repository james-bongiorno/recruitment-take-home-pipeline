# Challenge 1: Event RSVP API

**Time box: about 70 minutes of work** (you have 48 hours to send it back). Please stop at about 90 minutes even if you're not finished, and tell us what you'd do next. We care more about clear, working code than about finishing everything.

## The situation

A small venue runs events with limited seats. People RSVP for themselves and up to three guests. When an event is full, new RSVPs go on a waitlist, and when someone cancels, people on the waitlist get their seats. Your job is to build those rules and a small API around them.

## What's already here

```
app/store.py   Event and Rsvp, plus an in-memory store with two sample events (done)
app/rsvps.py   The rules you'll write: register(), cancel(), summary()
app/main.py    FastAPI app with a working /health endpoint
tests/         Fixtures (a fresh store, a 4-seat event, an API client) and a few starter tests
```

Setup (Python 3.11+):

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest            # the health test passes; the others fail until you write register()
uvicorn app.main:app --reload   # then open http://127.0.0.1:8000/docs
```

## Your tasks

1. **The rules, in `app/rsvps.py`:**
   - **`register(store, event, name, email, party_size)`**
     - The name is required. Emails are trimmed and lowercased.
     - An email needs text before a single `@` and a `.` in the part after it. Anything else raises `InvalidRsvp`.
     - `party_size` is 1 to 4 (the person plus up to three guests). Anything else raises `InvalidRsvp`.
     - One RSVP per email per event, whether confirmed or waitlisted. A second one raises `DuplicateRsvp`.
     - The RSVP is `"confirmed"` if the **whole party** fits in the remaining seats, otherwise `"waitlisted"`. Parties are never split.
   - **`cancel(store, event, rsvp_id)`**
     - Removes the RSVP, or raises `KeyError` if there isn't one with that id for this event.
     - If it was confirmed, go through the waitlist **in the order people joined** and confirm each party that fits in the free seats. A party that doesn't fit keeps its place, and you carry on to the next one.
     - Returns the ids that were promoted.
   - **`summary(store, event)`** returns `capacity`, `confirmed_seats`, `waitlisted_seats` and `remaining_seats`.
2. **The API, in `app/main.py`:**
   - `GET /events/{event_id}` returns the event's `id`, `name` and summary, or **404**.
   - `POST /events/{event_id}/rsvps` takes JSON `{"name", "email", "party_size"}` and returns **201** with the RSVP. It returns **400** for bad input, **404** for an unknown event and **409** for a duplicate.
   - `DELETE /events/{event_id}/rsvps/{rsvp_id}` returns **200** with `{"promoted": [ids]}`, or **404**.
3. **Tests.** Add tests for at least: a duplicate email (409 from the API), promotion after a cancellation, a party that's too big to promote while a smaller one behind it fits, and an unknown event (404).
4. **`NOTES.md`** (5–10 lines): decisions you made, anything you'd change with more time, and roughly how long you spent.

## Ground rules

- Keep to the libraries in `requirements.txt` unless you explain why in NOTES.md.
- Documentation and search are fine. If you use an AI assistant, say where in NOTES.md. We'll ask you to walk through your code either way.
- Send it back as a zip or a link to a private GitHub repo. Please don't post it publicly.

## Optional, only if you have time left

Two people RSVP for the last seats at the same moment. What could go wrong with your code, and how would you prevent it with a real database?
