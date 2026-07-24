import asyncio
import random

from src import client
from altamino.utils import log

ONLINE_INTERVAL = 60        
REFRESH_INTERVAL = 15 * 60

_communities: list[int] = []


async def _fetch_communities() -> list[int]:
    """Fetch all joined community ids, paginated."""
    result: list[int] = []
    start = 0
    size = 25

    while True:
        chunk = await client.get_joined_communities(start=start, size=size)
        if not chunk:
            break
        result.extend(c.comId for c in chunk)
        if len(chunk) < size:
            break
        start += size

    return result


async def refresh_task():
    global _communities
    while client.sid is None:
        await asyncio.sleep(1)

    while True:
        try:
            _communities = await _fetch_communities()
            log.debug(f"[online] Loaded {len(_communities)} communities")
        except Exception as e:
            log.error(f"[online] Failed to refresh communities: {e}")

        await asyncio.sleep(REFRESH_INTERVAL)


async def online_task():
    while not _communities:
        await asyncio.sleep(1)
    log.info(f"[altamino] Online task started")
    while True:
        communities = list(_communities)

        for com_id in communities:
            try:
                await client.online(com_id)
            except Exception as e:
                log.error(f"[online] comId={com_id}: {e}")

            await asyncio.sleep(random.uniform(0.5, 1.5))

        await asyncio.sleep(ONLINE_INTERVAL)


def start_background_online_tasks() -> list[asyncio.Task]:
    return [
        asyncio.create_task(refresh_task()),
        asyncio.create_task(online_task()),
    ]