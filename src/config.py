from dotenv import load_dotenv
import os
from time import time

load_dotenv()

ALTAMINO_RELOGIN_TIMEOUT = int(os.getenv("ALTAMINO_RELOGIN_TIMEOUT", "3600"))
ALTAMINO_RELOGIN_HITTED_TIMEOUT = int(os.getenv("ALTAMINO_RELOGIN_HITTED_TIMEOUT", "60"))



ALTAMINO_EMAIL: str = os.getenv("ALTAMINO_EMAIL")
ALTAMINO_PASSWORD: str = os.getenv("ALTAMINO_PASSWORD")
ALTAMINO_CLIENT_TYPE: int = int(os.getenv("ALTAMINO_CLIENT_TYPE", "100"))
ALTAMINO_DEVICE_ID: str = os.getenv("ALTAMINO_DEVICE_ID")


LOG_LVL: str = os.getenv("LOG_LVL", "20")
ENABLE_FILE_LOGGING: str = os.getenv("ENABLE_FILE_LOGGING", "0")

STARTUP = time()


DB_PATH = os.getenv("DB_PATH", "bot.db")

DEV_MODE = bool(int(os.getenv("DEV_MODE", "0")))
STATIC_BOT_VERSION = "beta 0.0.2"
BOT_VERSION = os.getenv("BOT_VERSION", STATIC_BOT_VERSION)

DEV_USERS = [
    "188d7b9a-0c98-4b54-9f98-c4ff434425c4",
]


FLOOD_LIMIT = 7
FLOOD_WINDOW = 5.0
IGNORE_TIME = 30.0