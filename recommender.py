"""Content-based recommender: TF-IDF-weighted genre vectors + a taste profile
built from the user's ratings (centred on 3, so low ratings push away)."""
import math
from collections import Counter

KINDS = ("film", "show", "anime", "book")


def _features(item):
    vec = {g.strip().lower(): 1.0 for g in item["genres"].split(",") if g.strip()}
    vec["kind:" + item["kind"]] = 0.5  # weak nudge toward same medium
    return vec


def _idf(items):
    df = Counter()
    for it in items:
        df.update(_features(it).keys())
    n = len(items)
    return {t: math.log((1 + n) / (1 + c)) + 1 for t, c in df.items()}


def _cosine(a, b):
    dot = sum(w * b.get(t, 0.0) for t, w in a.items())
    na = math.sqrt(sum(w * w for w in a.values()))
    nb = math.sqrt(sum(w * w for w in b.values()))
    return dot / (na * nb) if na and nb else 0.0


def recommend(items, ratings, kind=None, limit=12):
    """items: list of dict-like rows. ratings: {item_id: 1..5}.
    Returns [{"item", "score" (0-100), "reason"}] best first."""
    idf = _idf(items)
    vecs = {it["id"]: {t: w * idf[t] for t, w in _features(it).items()} for it in items}

    profile = Counter()
    for item_id, r in ratings.items():
        for t, w in vecs.get(item_id, {}).items():
            profile[t] += (r - 3) * w

    if not any(v > 0 for v in profile.values()):
        return []  # nothing liked yet (rate something 4-5 first)

    out = []
    for it in items:
        if it["id"] in ratings or (kind and it["kind"] != kind):
            continue
        vec = vecs[it["id"]]
        score = _cosine(profile, vec)
        if score <= 0:
            continue
        shared = sorted(
            (t for t in vec if profile.get(t, 0) > 0 and not t.startswith("kind:")),
            key=lambda t: profile[t], reverse=True,
        )[:2]
        reason = "Matches your taste for " + " and ".join(shared) if shared else "Similar medium to what you rate highly"
        out.append({"item": it, "score": round(score * 100), "reason": reason})

    out.sort(key=lambda r: r["score"], reverse=True)
    return out[:limit]
