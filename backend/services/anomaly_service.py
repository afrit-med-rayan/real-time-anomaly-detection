"""
backend/services/anomaly_service.py
-----------------------------------
In-memory datastore for recently scored events.
Used by the Kafka consumer to persist enriched transaction results,
and by the FastAPI application to query recent transactions.

For a production environment, this would be replaced with Redis or a database.
"""

from collections import deque
from typing import List, Dict

# ─── Config ───────────────────────────────────────────────────────────────

MAX_EVENTS = 1000

# ─── In-memory state ──────────────────────────────────────────────────────

# Thread-safe deque (for appends and pops off opposite ends)
_events_queue: deque = deque(maxlen=MAX_EVENTS)


def store_event(event: Dict) -> None:
    """
    Append an enriched event to the global list.
    If the list exceeds MAX_EVENTS, the oldest event is automatically dropped.
    """
    _events_queue.appendleft(event)


def get_recent_events(limit: int = 100) -> List[Dict]:
    """
    Retrieve the latest processed events.
    Returns up to `limit` events from newest to oldest.
    """
    events = list(_events_queue)
    return events[:limit]


def clear_events() -> None:
    """Clear all events (mostly useful for testing)."""
    _events_queue.clear()
