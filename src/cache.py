"""In-memory query result cache (experimental — not yet merged to main)."""

CACHE_TTL_SECONDS = 300
_store: dict = {}


def cache_query(key: str, result: object) -> None:
    """Store a query result under the given key."""
    import time
    _store[key] = {"result": result, "ts": time.time()}


def get_cached(key: str) -> object:
    """Return a cached result if still fresh, else None."""
    import time
    entry = _store.get(key)
    if entry and (time.time() - entry["ts"]) < CACHE_TTL_SECONDS:
        return entry["result"]
    return None
