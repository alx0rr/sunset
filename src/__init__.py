from altamino import log, AsyncClient, set_log_level, enable_file_logging
from asyncio import gather
from src.utils.cache import TTLCache
from src.utils.db import get_community_settings

from src.config import ALTAMINO_DEVICE_ID, ENABLE_FILE_LOGGING, LOG_LVL

set_log_level(int(LOG_LVL))
if int(ENABLE_FILE_LOGGING):
    enable_file_logging()

client = AsyncClient(ALTAMINO_DEVICE_ID)

community_cache = TTLCache(ttl=1200)
chat_cache = TTLCache(ttl=600)

async def warmup_cache():
    communities = await client.get_joined_communities(size=100)
    tasks = []
    for com in communities:
        comId = com.comId
        tasks.append(_cache_community(comId))
    await gather(*tasks)


async def _cache_community(comId):
    info = await client.get_community_info(comId)
    data = {
        "info": info,
        "settings": await get_community_settings(comId)
    }
    community_cache.set(comId, data)




async def wait():
    await client.socket_wait()