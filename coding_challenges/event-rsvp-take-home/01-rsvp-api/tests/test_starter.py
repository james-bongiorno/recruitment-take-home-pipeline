from app.rsvps import register


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_rsvp_is_confirmed_when_it_fits(store, small_event):
    rsvp = register(store, small_event, "Ada", "ada@example.com", 3)
    assert rsvp.status == "confirmed"


def test_rsvp_is_waitlisted_when_the_party_does_not_fit(store, small_event):
    register(store, small_event, "Ada", "ada@example.com", 3)
    rsvp = register(store, small_event, "Grace", "grace@example.com", 2)
    assert rsvp.status == "waitlisted"


# TODO: add your tests here (see README.md, task 3)
