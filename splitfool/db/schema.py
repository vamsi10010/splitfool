"""Database schema definitions for Splitfool."""

SCHEMA_VERSION = 1

SCHEMA_SQL = """
-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_users_name ON users(name);

-- Bills table
CREATE TABLE IF NOT EXISTS bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    payer_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    tax REAL NOT NULL CHECK(tax >= 0),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (payer_id) REFERENCES users(id)
);
CREATE INDEX IF NOT EXISTS idx_bills_payer_id ON bills(payer_id);
CREATE INDEX IF NOT EXISTS idx_bills_created_at ON bills(created_at DESC);

-- Items table
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    cost REAL NOT NULL CHECK(cost > 0),
    FOREIGN KEY (bill_id) REFERENCES bills(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_items_bill_id ON items(bill_id);

-- Assignments table
CREATE TABLE IF NOT EXISTS assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    fraction REAL NOT NULL CHECK(fraction > 0 AND fraction <= 1),
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(item_id, user_id)
);
CREATE INDEX IF NOT EXISTS idx_assignments_item_id ON assignments(item_id);
CREATE INDEX IF NOT EXISTS idx_assignments_user_id ON assignments(user_id);

-- Settlements table
CREATE TABLE IF NOT EXISTS settlements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    settled_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    note TEXT
);
CREATE INDEX IF NOT EXISTS idx_settlements_settled_at ON settlements(settled_at DESC);

-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
INSERT OR IGNORE INTO schema_version (version) VALUES (1);
"""
