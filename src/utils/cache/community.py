from src import community_cache
from src.utils.db import update_community_settings


async def apply_community_settings(event, **kwargs):
    s = await update_community_settings(event.comId, **kwargs)
    entry = community_cache.get(event.comId)
    if entry:
        entry["settings"] = s
    return s