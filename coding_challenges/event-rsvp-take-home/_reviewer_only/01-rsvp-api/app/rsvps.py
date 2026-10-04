"""Reference solution (reviewer only). One reasonable answer, not the only one."""
from app.store import Event, Rsvp, Store

MAX_PARTY_SIZE = 4


class RsvpError(ValueError):
    """Base class for RSVP problems."""


class InvalidRsvp(RsvpError):
    """Bad input: email or party size."""


class DuplicateRsvp(RsvpError):
    """This email already has an RSVP for this event."""


def _valid_email(email: str) -> bool:
    local, at, domain = email.partition("@")
    return bool(at) and bool(local) and "@" not in domain and "." in domain.strip(".")


def _for_event(store: Store, event: Event) -> list[Rsvp]:
    return [r for r in store.rsvps if r.event_id == event.id]


def _confirmed_seats(store: Store, event: Event) -> int:
    return sum(r.party_size for r in _for_event(store, event) if r.status == "confirmed")


def register(store: Store, event: Event, name: str, email: str, party_size: int) -> Rsvp:
    name, email = (name or "").strip(), (email or "").strip().lower()
    if not name:
        raise InvalidRsvp("name is required")
    if not _valid_email(email):
        raise InvalidRsvp(f"{email!r} is not a valid email address")
    if not isinstance(party_size, int) or isinstance(party_size, bool) or not 1 <= party_size <= MAX_PARTY_SIZE:
        raise InvalidRsvp(f"party_size must be between 1 and {MAX_PARTY_SIZE}")
    if any(r.email == email for r in _for_event(store, event)):
        raise DuplicateRsvp(f"{email} already has an RSVP for this event")

    fits = _confirmed_seats(store, event) + party_size <= event.capacity
    rsvp = Rsvp(store.new_id(), event.id, name, email, party_size, "confirmed" if fits else "waitlisted")
    store.rsvps.append(rsvp)
    return rsvp


def cancel(store: Store, event: Event, rsvp_id: int) -> list[int]:
    rsvp = next((r for r in _for_event(store, event) if r.id == rsvp_id), None)
    if rsvp is None:
        raise KeyError(rsvp_id)
    store.rsvps.remove(rsvp)
    if rsvp.status != "confirmed":
        return []

    promoted = []
    remaining = event.capacity - _confirmed_seats(store, event)
    for waiting in _for_event(store, event):  # store.rsvps keeps join order
        if waiting.status == "waitlisted" and waiting.party_size <= remaining:
            waiting.status = "confirmed"
            remaining -= waiting.party_size
            promoted.append(waiting.id)
    return promoted


def summary(store: Store, event: Event) -> dict:
    confirmed = _confirmed_seats(store, event)
    waitlisted = sum(r.party_size for r in _for_event(store, event) if r.status == "waitlisted")
    return {"capacity": event.capacity, "confirmed_seats": confirmed,
            "waitlisted_seats": waitlisted, "remaining_seats": event.capacity - confirmed}
