"""In-memory data. Everything resets when the server restarts, which is fine here."""
from dataclasses import dataclass, field


@dataclass
class Event:
    id: str
    name: str
    capacity: int  # total seats


@dataclass
class Rsvp:
    id: int
    event_id: str
    name: str
    email: str
    party_size: int
    status: str  # "confirmed" or "waitlisted"


@dataclass
class Store:
    events: dict[str, Event] = field(default_factory=dict)
    rsvps: list[Rsvp] = field(default_factory=list)  # in the order they were made
    next_id: int = 1

    def new_id(self) -> int:
        self.next_id += 1
        return self.next_id - 1


def seeded_store() -> Store:
    store = Store()
    for event in [Event("jazz-night", "Jazz Night", 40), Event("pottery-101", "Pottery 101", 6)]:
        store.events[event.id] = event
    return store
