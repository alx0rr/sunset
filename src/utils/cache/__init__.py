import time
import asyncio
from typing import Any, Optional


class TTLCache:
    def __init__(self, ttl: float = 300):
        self.ttl = ttl
        self._store: dict[Any, tuple[float, Any]] = {}
        self._locks: dict[Any, asyncio.Lock] = {}
        self._lock = asyncio.Lock()

    async def _get_lock(self, key: Any) -> asyncio.Lock:
        async with self._lock:
            if key not in self._locks:
                self._locks[key] = asyncio.Lock()
            return self._locks[key]

    def get(self, key: Any) -> Optional[Any]:
        item = self._store.get(key)
        if item is None:
            return None
        ts, value = item
        if time.monotonic() - ts > self.ttl:
            return None
        return value

    def set(self, key: Any, value: Any):
        self._store[key] = (time.monotonic(), value)

    def is_stale(self, key: Any) -> bool:
        item = self._store.get(key)
        if item is None:
            return True
        return time.monotonic() - item[0] > self.ttl