import asyncio

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

from src import log
from src.utils.i18n import load_locales
from src.altamino import on_startup_altamino, on_altamino_shutdown
from src.telegram import on_startup_tg, on_tg_shutdown
from pyrogram import idle

async def start():
    log.info("Starting bot...")
    load_locales()
    await on_startup_tg()
    await on_startup_altamino()
    await idle()

    try:
        await on_altamino_shutdown()
    except Exception as e:
        log.error(f"[altamino] Shutdown error: {e}")

    try:
        await on_tg_shutdown()
    except Exception as e:
        log.error(f"[tg] Shutdown error: {e}")

if __name__ == "__main__":
    try:
        loop.run_until_complete(start())
    finally:
        loop.close()