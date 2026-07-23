
from src import client
from src import log
from src.utils.loader import load_altamino_modules
from src.aa.relogin import relogin_task
from asyncio import create_task

task_relogin = None


async def on_startup_altamino():
    global task_relogin
    load_altamino_modules()
    task_relogin = create_task(relogin_task())

async def on_altamino_shutdown():
    log.info("[altamino] Shutdown...")
    if task_relogin: task_relogin.cancel()
    await client.logout()