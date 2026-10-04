"""Reference solution (reviewer only)."""
from dataclasses import asdict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.rsvps import DuplicateRsvp, InvalidRsvp, cancel, register, summary
from app.store import Event, seeded_store

app = FastAPI(title="Event RSVPs")
store = seeded_store()


class RsvpIn(BaseModel):
    name: str
    email: str
    party_size: int


def _event(event_id: str) -> Event:
    event = store.events.get(event_id)
    if event is None:
        raise HTTPException(404, f"No event with id {event_id!r}")
    return event


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/events/{event_id}")
def get_event(event_id: str) -> dict:
    event = _event(event_id)
    return {"id": event.id, "name": event.name, **summary(store, event)}


@app.post("/events/{event_id}/rsvps", status_code=201)
def create_rsvp(event_id: str, body: RsvpIn) -> dict:
    event = _event(event_id)
    try:
        return asdict(register(store, event, body.name, body.email, body.party_size))
    except InvalidRsvp as err:
        raise HTTPException(400, str(err)) from None
    except DuplicateRsvp as err:
        raise HTTPException(409, str(err)) from None


@app.delete("/events/{event_id}/rsvps/{rsvp_id}")
def delete_rsvp(event_id: str, rsvp_id: int) -> dict:
    event = _event(event_id)
    try:
        return {"promoted": cancel(store, event, rsvp_id)}
    except KeyError:
        raise HTTPException(404, f"No RSVP {rsvp_id} for this event") from None
