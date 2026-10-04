-- Ticket sales. Applied by sales.db.connect() every time it opens a database.

CREATE TABLE IF NOT EXISTS events (
    id           INTEGER PRIMARY KEY,
    name         TEXT    NOT NULL,
    capacity     INTEGER NOT NULL CHECK (capacity > 0),
    price_cents  INTEGER NOT NULL CHECK (price_cents >= 0)
);

-- TODO (task 2): this table works, but it trusts the Python code completely.
-- Add constraints so the database itself refuses bad orders. See README.md.
CREATE TABLE IF NOT EXISTS orders (
    id                INTEGER PRIMARY KEY,
    event_id          INTEGER,
    buyer_email       TEXT,
    quantity          INTEGER,
    unit_price_cents  INTEGER,
    coupon            TEXT,
    created_at        TEXT DEFAULT CURRENT_TIMESTAMP
);
