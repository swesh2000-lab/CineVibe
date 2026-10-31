import sqlite3
from pathlib import Path

from titles import TITLES

DB_PATH = Path(__file__).parent / "recommender.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    id          INTEGER PRIMARY KEY,
    title       TEXT NOT NULL,
    kind        TEXT NOT NULL CHECK (kind IN ('film','show','anime','book')),
    year        INTEGER,
    genres      TEXT NOT NULL,          -- comma-separated
    description TEXT
);
CREATE TABLE IF NOT EXISTS ratings (
    item_id   INTEGER PRIMARY KEY REFERENCES items(id) ON DELETE CASCADE,
    rating    INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    rated_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS watchlist (
    item_id   INTEGER PRIMARY KEY REFERENCES items(id) ON DELETE CASCADE,
    added_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)
        existing = {
            (row["title"], row["kind"])
            for row in conn.execute("SELECT title, kind FROM items")
        }
        new_rows = [t for t in TITLES if (t[0], t[1]) not in existing]
        conn.executemany(
            "INSERT INTO items (title, kind, year, genres, description) VALUES (?,?,?,?,?)",
            new_rows,
        )
