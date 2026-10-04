"""RSVP rules. See README.md for the full rules."""
from app.store import Event, Rsvp, Store

MAX_PARTY_SIZE = 4


class RsvpError(ValueError):
    """Base class for RSVP problems."""


class InvalidRsvp(RsvpError):
    """Bad input: email or party size."""


class DuplicateRsvp(RsvpError):
    """This email already has an RSVP for this event."""


def register(store: Store, event: Event, name: str, email: str, party_size: int) -> Rsvp:
    """Add an RSVP, confirmed if the whole party fits, otherwise waitlisted."""
    # TODO (task 1)
    raise NotImplementedError


def cancel(store: Store, event: Event, rsvp_id: int) -> list[int]:
    """Remove an RSVP. If it was confirmed, promote waitlisted parties. Returns promoted RSVP ids.
    Raises KeyError if there's no such RSVP for this event."""
    # TODO (task 1)
    raise NotImplementedError


def summary(store: Store, event: Event) -> dict:
    """{"capacity", "confirmed_seats", "waitlisted_seats", "remaining_seats"}"""
    # TODO (task 1)
    raise NotImplementedError
