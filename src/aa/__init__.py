
from src import client
from src import log
from src.utils.loader import load_altamino_modules
from src.aa.relogin import relogin_task
from asyncio import create_task
from src.aa.online import start_background_online_tasks

task_relogin = None
task_online = None
task_refresh_com = None

async def on_startup_altamino():
    global task_relogin
    global task_online
    global task_refresh_com
    
    load_altamino_modules()
    task_relogin = create_task(relogin_task())
    task_refresh_com, task_online = start_background_online_tasks()

async def on_altamino_shutdown():
    global task_relogin
    global task_online
    global task_refresh_com
    log.info("[altamino] Shutdown...")
    if task_relogin: task_relogin.cancel()
    if task_online: task_online.cancel()
    if task_refresh_com: task_refresh_com.cancel()
    await client.logout()