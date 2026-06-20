from dotenv import load_dotenv
import os

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")



ALTAMINO_RELOGIN_TIMEOUT = int(os.getenv("ALTAMINO_RELOGIN_TIMEOUT", "3600"))
ALTAMINO_RELOGIN_HITTED_TIMEOUT = int(os.getenv("ALTAMINO_RELOGIN_HITTED_TIMEOUT", "60"))




ALTAMINO_EMAIL: str = os.getenv("ALTAMINO_EMAIL")
ALTAMINO_PASSWORD: str = os.getenv("ALTAMINO_PASSWORD")
ALTAMINO_CLIENT_TYPE: int = int(os.getenv("ALTAMINO_CLIENT_TYPE", "100"))
ALTAMINO_DEVICE_ID: str = os.getenv("ALTAMINO_DEVICE_ID")


LOG_LVL: str = os.getenv("LOG_LVL", "20")
ENABLE_FILE_LOGGING: str = os.getenv("ENABLE_FILE_LOGGING", "0")