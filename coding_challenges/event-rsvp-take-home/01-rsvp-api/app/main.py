from fastapi import FastAPI

from app.rsvps import DuplicateRsvp, InvalidRsvp, cancel, register, summary  # noqa: F401  (you'll need these)
from app.store import seeded_store

app = FastAPI(title="Event RSVPs")
store = seeded_store()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


# TODO (task 2):
#   GET    /events/{event_id}                    event details plus summary(), or 404
#   POST   /events/{event_id}/rsvps              JSON {"name", "email", "party_size"} -> 201 with the RSVP
#                                                400 bad input, 404 unknown event, 409 duplicate email
#   DELETE /events/{event_id}/rsvps/{rsvp_id}    200 {"promoted": [ids]}, or 404
