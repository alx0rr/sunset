from pyrogram.types import Message

from src.utils.i18n import t



async def handle_chat(reply: Message, link_info, lang) -> None:
    await reply.edit_text(t("telegram.links.unsupported", lang))
