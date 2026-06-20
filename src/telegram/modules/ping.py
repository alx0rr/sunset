from pyrogram import filters
from pyrogram.types import Message

from src.telegram import tgApp as app

@app.on_message(filters.command("ping"))
async def ping_handler(_, message: Message):
    await message.reply("pong")