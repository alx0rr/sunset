from altamino import log, AsyncClient, set_log_level, enable_file_logging

from src.config import ALTAMINO_DEVICE_ID, ENABLE_FILE_LOGGING, LOG_LVL

set_log_level(int(LOG_LVL))
if int(ENABLE_FILE_LOGGING):
    enable_file_logging()

client = AsyncClient(ALTAMINO_DEVICE_ID)



async def wait():
    await client.socket_wait()