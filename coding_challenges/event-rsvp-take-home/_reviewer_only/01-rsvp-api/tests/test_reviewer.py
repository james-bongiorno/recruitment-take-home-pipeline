"""Extra checks (reviewer only). Copy into the candidate's tests/ folder and run pytest."""
import pytest

from app.rsvps import DuplicateRsvp, InvalidRsvp, cancel, register, summary


def test_email_is_normalized_and_duplicates_rejected(store, small_event):
    register(store, small_event, "Ada", "  Ada@Example.COM ", 1)
    with pytest.raises(DuplicateRsvp):
        register(store, small_event, "Ada again", "ada@example.com", 1)


def test_duplicate_check_includes_the_waitlist(store, small_event):
    register(store, small_event, "Ada", "ada@example.com", 4)
    register(store, small_event, "Grace", "grace@example.com", 2)  # waitlisted
    with pytest.raises(DuplicateRsvp):
        register(store, small_event, "Grace", "grace@example.com", 1)


@pytest.mark.parametrize("email", ["", "ada", "ada@", "@example.com", "ada@example", "a@b@c.com"])
def test_bad_emails(store, small_event, email):
    with pytest.raises(InvalidRsvp):
        register(store, small_event, "Ada", email, 1)


@pytest.mark.parametrize("size", [0, 5, -1])
def test_bad_party_sizes(store, small_event, size):
    with pytest.raises(InvalidRsvp):
        register(store, small_event, "Ada", "ada@example.com", size)


def test_exactly_full_is_confirmed(store, small_event):
    register(store, small_event, "Ada", "ada@example.com", 2)
    assert register(store, small_event, "Grace", "grace@example.com", 2).status == "confirmed"


def test_cancel_promotes_waitlisted_parties_in_join_order(store, small_event):
    a = register(store, small_event, "Ada", "ada@example.com", 4)
    w1 = register(store, small_event, "W1", "w1@example.com", 2)
    w2 = register(store, small_event, "W2", "w2@example.com", 2)
    w3 = register(store, small_event, "W3", "w3@example.com", 1)
    assert cancel(store, small_event, a.id) == [w1.id, w2.id]
    assert w3.status == "waitlisted"


def test_cancel_skips_a_big_party_for_a_smaller_one(store, small_event):
    a = register(store, small_event, "Ada", "ada@example.com", 2)
    register(store, small_event, "Bo", "bo@example.com", 2)
    big = register(store, small_event, "Big", "big@example.com", 3)        # waitlisted
    small = register(store, small_event, "Small", "small@example.com", 2)  # waitlisted
    assert cancel(store, small_event, a.id) == [small.id]
    assert big.status == "waitlisted"


def test_cancelling_a_waitlisted_rsvp_promotes_nobody(store, small_event):
    register(store, small_event, "Ada", "ada@example.com", 4)
    w = register(store, small_event, "Grace", "grace@example.com", 1)
    assert cancel(store, small_event, w.id) == []


def test_summary(store, small_event):
    register(store, small_event, "Ada", "ada@example.com", 3)
    register(store, small_event, "Grace", "grace@example.com", 2)
    assert summary(store, small_event) == {"capacity": 4, "confirmed_seats": 3,
                                           "waitlisted_seats": 2, "remaining_seats": 1}


def test_api_round_trip(client, store):
    r = client.post("/events/pottery-101/rsvps", json={"name": "Ada", "email": "ada@example.com", "party_size": 4})
    assert r.status_code == 201 and r.json()["status"] == "confirmed"
    rsvp_id = r.json()["id"]
    r = client.post("/events/pottery-101/rsvps", json={"name": "Lin", "email": "lin@example.com", "party_size": 3})
    assert r.json()["status"] == "waitlisted"
    assert client.get("/events/pottery-101").json()["remaining_seats"] == 2
    assert client.delete(f"/events/pottery-101/rsvps/{rsvp_id}").json() == {"promoted": [r.json()["id"]]}


def test_api_errors(client, store):
    body = {"name": "Ada", "email": "ada@example.com", "party_size": 2}
    assert client.post("/events/nope/rsvps", json=body).status_code == 404
    assert client.get("/events/nope").status_code == 404
    assert client.post("/events/jazz-night/rsvps", json={**body, "party_size": 9}).status_code == 400
    assert client.post("/events/jazz-night/rsvps", json={**body, "email": "bad"}).status_code == 400
    assert client.post("/events/jazz-night/rsvps", json=body).status_code == 201
    assert client.post("/events/jazz-night/rsvps", json=body).status_code == 409
    assert client.delete("/events/jazz-night/rsvps/999").status_code == 404
