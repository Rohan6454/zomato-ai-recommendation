from __future__ import annotations

import time
from typing import Any, Dict, Optional, Tuple


class TTLCache:
    def __init__(self, ttl_seconds: int = 60, max_items: int = 512):
        self._ttl = ttl_seconds
        self._max_items = max_items
        self._store: Dict[str, Tuple[float, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        now = time.time()
        item = self._store.get(key)
        if not item:
            return None
        expires_at, value = item
        if expires_at < now:
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        if len(self._store) >= self._max_items:
            # Simple eviction: remove one arbitrary expired item first, else arbitrary key.
            now = time.time()
            removed = False
            for k, (exp, _) in list(self._store.items()):
                if exp < now:
                    self._store.pop(k, None)
                    removed = True
                    break
            if not removed and self._store:
                self._store.pop(next(iter(self._store)))
        self._store[key] = (time.time() + self._ttl, value)

