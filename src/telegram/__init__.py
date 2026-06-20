from src import log, tgApp
from src.utils.loader import load_tg_modules

async def on_startup_tg():
    load_tg_modules(tgApp)
    await tgApp.start()

    me = await tgApp.get_me()

    log.info(f"[tg] Bot started as @{me.username}")
    log.info(f"[tg] Bot ID: {me.id}")
    log.info(f"[tg] Name: {me.first_name}")
    

async def on_tg_shutdown():
    log.info("[tg] Shutdown...")
    await tgApp.stop()