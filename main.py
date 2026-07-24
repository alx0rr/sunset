import asyncio

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

from src import log, wait, warmup_cache
from src.utils.greeting_image import load_image_assets
from src.aa import on_altamino_shutdown, on_startup_altamino
from src.utils.i18n import load_locales
from src.utils.db import  init_db


async def start():
    log.info("Starting bot...")
    load_locales()
    log.info(f"[main] Locales loaded")
    await init_db()
    log.info(f"[main] Db initialized")
    await on_startup_altamino()
    log.info(f"[main] altamino client initialized")
    await warmup_cache()
    log.info(f"[main] Cache warmuped")
    await load_image_assets()
    log.info(f"[main] Assets loaded")

    await wait()

    try:
        await on_altamino_shutdown()
    except Exception as e:
        log.error(f"[altamino] Shutdown error: {e}")

    pending = [t for t in asyncio.all_tasks(loop=loop) if t is not asyncio.current_task()]
    
    if pending:
        log.info(f"[main] Cleaning up {len(pending)} pending tasks...")
        for task in pending:
            task.cancel()
        
        await asyncio.gather(*pending, return_exceptions=True)


if __name__ == "__main__":
    try:
        loop.run_until_complete(start())
    finally:
        loop.close()
        log.info("[main] Loop closed cleanly.")