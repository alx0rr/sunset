from pyrogram import Client
from altamino import log, AsyncClient, set_log_level, enable_file_logging

from src.config import API_ID, API_HASH, BOT_TOKEN, ALTAMINO_DEVICE_ID, ENABLE_FILE_LOGGING, LOG_LVL

set_log_level(int(LOG_LVL))
if int(ENABLE_FILE_LOGGING):
    enable_file_logging()

tgApp = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

altAminoClient = AsyncClient(ALTAMINO_DEVICE_ID)

