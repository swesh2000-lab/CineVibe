import sqlite3
from pathlib import Path

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
"""

SEED = [
    ("Blade Runner", "film", 1982, "sci-fi, noir, philosophical", "A hunter tracks synthetic humans through a rain-soaked future city."),
    ("Arrival", "film", 2016, "sci-fi, drama, philosophical", "A linguist tries to decode an alien language before the world panics."),
    ("Parasite", "film", 2019, "thriller, drama, satire", "A poor family infiltrates a wealthy household."),
    ("The Godfather", "film", 1972, "crime, drama, epic", "A crime dynasty passes from father to reluctant son."),
    ("Spirited Away", "film", 2001, "fantasy, adventure, coming-of-age", "A girl works in a bathhouse for spirits to free her parents."),
    ("Mad Max: Fury Road", "film", 2015, "action, sci-fi, adventure", "A desert chase across a wasteland."),
    ("Se7en", "film", 1995, "thriller, crime, noir", "Two detectives chase a killer using the seven deadly sins."),
    ("The Truman Show", "film", 1998, "drama, satire, philosophical", "A man discovers his whole life is a broadcast."),
    ("Breaking Bad", "show", 2008, "crime, drama, thriller", "A chemistry teacher turns to making drugs."),
    ("The Wire", "show", 2002, "crime, drama, realistic", "Police and dealers in Baltimore, seen from every side."),
    ("Chernobyl", "show", 2019, "drama, historical, thriller", "The 1986 nuclear disaster and the cover-up."),
    ("Black Mirror", "show", 2011, "sci-fi, satire, thriller", "Standalone stories about technology gone wrong."),
    ("Succession", "show", 2018, "drama, satire, family", "Siblings fight to inherit a media empire."),
    ("Severance", "show", 2022, "sci-fi, thriller, philosophical", "Workers split their memories between job and home."),
    ("Death Note", "anime", 2006, "thriller, supernatural, psychological", "A student finds a notebook that kills."),
    ("Monster", "anime", 2004, "thriller, psychological, crime", "A surgeon hunts a boy he once saved."),
    ("Cowboy Bebop", "anime", 1998, "sci-fi, action, noir", "Bounty hunters drift through space."),
    ("Vinland Saga", "anime", 2019, "historical, action, drama", "A Viking boy's revenge turns into a search for meaning."),
    ("Mushishi", "anime", 2005, "fantasy, philosophical, slice-of-life", "A wanderer studies strange life forms."),
    ("Fullmetal Alchemist: Brotherhood", "anime", 2009, "fantasy, adventure, action", "Two brothers seek the Philosopher's Stone."),
    ("Dune", "book", 1965, "sci-fi, epic, philosophical", "Politics, religion and ecology on a desert planet."),
    ("1984", "book", 1949, "dystopian, philosophical, political", "A man resists total surveillance."),
    ("Crime and Punishment", "book", 1866, "crime, psychological, philosophical", "A student commits murder and unravels."),
    ("The Name of the Wind", "book", 2007, "fantasy, adventure, coming-of-age", "A legend tells his own story."),
    ("Sapiens", "book", 2011, "historical, nonfiction, philosophical", "A short history of humankind."),
]


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)
        if conn.execute("SELECT COUNT(*) FROM items").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO items (title, kind, year, genres, description) VALUES (?,?,?,?,?)",
                SEED,
            )
