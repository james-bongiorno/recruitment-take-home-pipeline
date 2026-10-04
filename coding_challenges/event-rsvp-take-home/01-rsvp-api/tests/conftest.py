import pytest
from fastapi.testclient import TestClient

import app.main
from app.store import Event, seeded_store


@pytest.fixture
def store():
    """A fresh store for each test, also used by the API."""
    fresh = seeded_store()
    app.main.store = fresh
    return fresh


@pytest.fixture
def small_event(store):
    """An event with 4 seats."""
    event = Event("tiny-show", "Tiny Show", 4)
    store.events[event.id] = event
    return event


@pytest.fixture
def client(store):
    return TestClient(app.main.app)
