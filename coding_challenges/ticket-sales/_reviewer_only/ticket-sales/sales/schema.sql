-- Reference schema (reviewer only).

CREATE TABLE IF NOT EXISTS events (
    id           INTEGER PRIMARY KEY,
    name         TEXT    NOT NULL,
    capacity     INTEGER NOT NULL CHECK (capacity > 0),
    price_cents  INTEGER NOT NULL CHECK (price_cents >= 0)
);

CREATE TABLE IF NOT EXISTS orders (
    id                INTEGER PRIMARY KEY,
    event_id          INTEGER NOT NULL REFERENCES events (id),  -- no cascade: events with sales can't be deleted
    buyer_email       TEXT    NOT NULL CHECK (buyer_email LIKE '%_@_%'),
    quantity          INTEGER NOT NULL CHECK (quantity BETWEEN 1 AND 10),
    unit_price_cents  INTEGER NOT NULL CHECK (unit_price_cents >= 0),
    coupon            TEXT,
    created_at        TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS orders_by_event ON orders (event_id);
