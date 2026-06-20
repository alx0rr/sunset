
from src import altAminoClient as client
from src import log
from src.utils.loader import load_altamino_modules
from src.config import ALTAMINO_EMAIL, ALTAMINO_PASSWORD, ALTAMINO_CLIENT_TYPE
from sys import exit


async def on_startup_altamino():
    try:
        load_altamino_modules()
        await client.login(ALTAMINO_EMAIL, ALTAMINO_PASSWORD, client_type=ALTAMINO_CLIENT_TYPE)
        log.info(f"[altamino] Logged in as {ALTAMINO_EMAIL}")
    except Exception as e:
        log.critical(f"[altamino] Login failed: {e}")
        exit()

async def on_altamino_shutdown():
    log.info("[altamino] Shutdown...")
    await client.logout()