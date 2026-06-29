import base64
from datetime import datetime, timezone

from pyrogram import filters
from pyrogram.types import Message

from src.telegram import tgApp as app
from src.utils import ping_text
from src.utils.db import get_language
from src.utils.i18n import t
from src.telegram.helpers.wrappers.adm import is_admin
from src.telegram.modules.adm import link_altamino, unlink_altamino
from src.config import LINKING_SECRET_KEY

TOKEN_TTL_MS = 120000

@app.on_message(filters.command("ping"))
async def ping_handler(_, message: Message):
    start = datetime.now(timezone.utc)
    reply = await message.reply("🏓 Pinging...")
    latency_ms = (datetime.now(timezone.utc) - start).total_seconds() * 1000
    await reply.edit_text("**🏓Pong!**\n\n" + ping_text(latency_ms))

@app.on_message(filters.command("help"))
async def help_handler(_, message: Message):
    lang = get_language(message.from_user.id)
    await message.reply(t("telegram.help", lang))

@app.on_message(filters.command("start"))
async def start_handler(_, message: Message):
    lang = get_language(message.from_user.id)
    tg_id = message.from_user.id
    
    if len(message.command) <= 1:
        await message.reply(t("telegram.welcome", lang))
        return

    payload = message.command[1]
    
    if not (payload.startswith("link-account:") or payload.startswith("unlink-account:")):
        await message.reply(t("telegram.welcome", lang))
        return
        
    if not is_admin(tg_id):
        await message.reply(t("telegram.admin_only", lang))
        return

    try:
        action, base64_token = payload.split(":", 1)
        
        missing_padding = len(base64_token) % 4
        if missing_padding:
            base64_token += '=' * (4 - missing_padding)
            
        decoded_bytes = base64.urlsafe_b64decode(base64_token)
        decoded_str = decoded_bytes.decode("utf-8")
        
        amino_id, timestamp_str, secret_token = decoded_str.split(":", 2)
        timestamp = int(timestamp_str)
    except Exception:
        await message.reply(t("telegram.errors.invalid_token", lang))
        return

    if secret_token != LINKING_SECRET_KEY:
        await message.reply(t("telegram.errors.invalid_token", lang))
        return

    current_time_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    if abs(current_time_ms - timestamp) > TOKEN_TTL_MS:
        await message.reply(t("telegram.errors.token_expired", lang))
        return

    if action == "link-account":
        try:
            await link_altamino(amino_id, tg_id)
            await message.reply(t("telegram.success.linked", lang))
        except Exception:
            await message.reply(t("telegram.errors.link_failed", lang))
            
    elif action == "unlink-account":
        try:
            await unlink_altamino(amino_id)
            await message.reply(t("telegram.success.unlinked", lang))
        except Exception:
            await message.reply(t("telegram.errors.unlink_failed", lang))