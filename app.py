from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from db import get_conn, init_db
from recommender import KINDS, recommend

BASE = Path(__file__).parent

SORTS = {
    "title": "title COLLATE NOCASE ASC",
    "newest": "year DESC, title COLLATE NOCASE ASC",
    "oldest": "year ASC, title COLLATE NOCASE ASC",
}


@asynccontextmanager
async def lifespan(app):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")


def _ratings(conn):
    return {r["item_id"]: r["rating"] for r in conn.execute("SELECT item_id, rating FROM ratings")}


def _render(request, name, **ctx):
    return templates.TemplateResponse(request, name, {"kinds": KINDS, **ctx})


@app.get("/")
def browse(request: Request, kind: str | None = None, q: str = "", genre: str = "", sort: str = "title"):
    if sort not in SORTS:
        sort = "title"
    with get_conn() as conn:
        all_genres = sorted(
            {g.strip() for row in conn.execute("SELECT genres FROM items") for g in row["genres"].split(",") if g.strip()}
        )
        sql, args = "SELECT * FROM items WHERE 1=1", []
        if kind in KINDS:
            sql += " AND kind = ?"
            args.append(kind)
        if q.strip():
            sql += " AND (title LIKE ? OR genres LIKE ?)"
            args += [f"%{q.strip()}%"] * 2
        if genre in all_genres:
            sql += " AND (',' || REPLACE(genres, ' ', '') || ',') LIKE ?"
            args.append(f"%,{genre},%")
        else:
            genre = ""
        items = conn.execute(sql + " ORDER BY " + SORTS[sort], args).fetchall()
        ratings = _ratings(conn)
    return _render(
        request, "index.html", items=items, ratings=ratings, kind=kind, q=q,
        genre=genre, sort=sort, all_genres=all_genres, page="browse",
    )


@app.get("/item/{item_id}")
def detail(request: Request, item_id: int):
    with get_conn() as conn:
        item = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
        if not item:
            raise HTTPException(404, "Item not found")
        rating = _ratings(conn).get(item_id)
        watching = conn.execute("SELECT 1 FROM watchlist WHERE item_id = ?", (item_id,)).fetchone() is not None
    return _render(request, "item.html", item=item, rating=rating, watching=watching, page="browse")


@app.post("/rate/{item_id}")
def rate(item_id: int, rating: int = Form(..., ge=1, le=5), next: str = Form("/")):
    with get_conn() as conn:
        if not conn.execute("SELECT 1 FROM items WHERE id = ?", (item_id,)).fetchone():
            raise HTTPException(404, "Item not found")
        conn.execute(
            "INSERT INTO ratings (item_id, rating) VALUES (?, ?) "
            "ON CONFLICT(item_id) DO UPDATE SET rating = excluded.rating, rated_at = CURRENT_TIMESTAMP",
            (item_id, rating),
        )
    return RedirectResponse(next if next.startswith("/") else "/", status_code=303)


@app.post("/unrate/{item_id}")
def unrate(item_id: int, next: str = Form("/")):
    with get_conn() as conn:
        conn.execute("DELETE FROM ratings WHERE item_id = ?", (item_id,))
    return RedirectResponse(next if next.startswith("/") else "/", status_code=303)


@app.get("/recommendations")
def recommendations(request: Request, kind: str | None = None):
    with get_conn() as conn:
        items = conn.execute("SELECT * FROM items").fetchall()
        ratings = _ratings(conn)
    recs = recommend(items, ratings, kind=kind if kind in KINDS else None)
    return _render(request, "recs.html", recs=recs, kind=kind, rated_count=len(ratings), page="recs")


@app.get("/rated")
def rated(request: Request):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT i.*, r.rating FROM ratings r JOIN items i ON i.id = r.item_id ORDER BY r.rated_at DESC"
        ).fetchall()
    return _render(request, "rated.html", rows=rows, page="rated")


@app.post("/watch/{item_id}")
def watch(item_id: int, next: str = Form("/")):
    with get_conn() as conn:
        if not conn.execute("SELECT 1 FROM items WHERE id = ?", (item_id,)).fetchone():
            raise HTTPException(404, "Item not found")
        conn.execute("INSERT OR IGNORE INTO watchlist (item_id) VALUES (?)", (item_id,))
    return RedirectResponse(next if next.startswith("/") else "/", status_code=303)


@app.post("/unwatch/{item_id}")
def unwatch(item_id: int, next: str = Form("/")):
    with get_conn() as conn:
        conn.execute("DELETE FROM watchlist WHERE item_id = ?", (item_id,))
    return RedirectResponse(next if next.startswith("/") else "/", status_code=303)


@app.get("/watchlist")
def watchlist(request: Request):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT i.* FROM watchlist w JOIN items i ON i.id = w.item_id ORDER BY w.added_at DESC"
        ).fetchall()
    return _render(request, "watchlist.html", rows=rows, page="watchlist")
