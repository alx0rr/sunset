from pyrogram import filters
from pyrogram.types import Message, ChatMemberUpdated
from src.telegram import tgApp as app
from src.utils.db import get_language
from src.utils.i18n import t


@app.on_message(filters.new_chat_members)
async def new_member_handler(_, message: Message):
    try:
        lang = get_language(message.chat.id, isChat=True)
        for member in message.new_chat_members:
            if member.id == (await app.get_me()).id:
                await message.reply(t("telegram.bot_added", lang))
            else:
                name = member.first_name or member.username or "Member"
                await message.reply(t("telegram.new_member", lang).format(name=name))
    except:pass