from src.config import ALTAMINO_RELOGIN_HITTED_TIMEOUT, ALTAMINO_RELOGIN_TIMEOUT, ALTAMINO_EMAIL, ALTAMINO_PASSWORD, ALTAMINO_CLIENT_TYPE
from src import altAminoClient as client
from altamino import log
from asyncio import sleep, CancelledError


async def relogin_task():
    log.info(f"[altamino] Relogin started")
    try:
        hit_happened = False
        while True:
            try:
                await client.logout()
                log.info(f"[altamino] Logged out")
            except Exception:
                log.critical(f"[altamino] Can't logout for some reason.")

            try:
                await client.login(ALTAMINO_EMAIL, ALTAMINO_PASSWORD, client_type=ALTAMINO_CLIENT_TYPE)
                log.info(f"[altamino] Logged in as {ALTAMINO_EMAIL}")
                hit_happened = False
            except Exception as e:
                hit_happened = True
                log.critical(f"[altamino] Can't relogin! Reason: {e}")


            if hit_happened:
                await sleep(ALTAMINO_RELOGIN_HITTED_TIMEOUT)
                continue

            await sleep(ALTAMINO_RELOGIN_TIMEOUT)

    except CancelledError:
        log.info("[altamino] Relogin cancelled")