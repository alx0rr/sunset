from pyrogram.types import Message

from src.utils.i18n import t



async def handle_wiki(reply: Message, link_info, lang) -> None:
    await reply.edit_text(t("telegram.links.unsupported", lang))

async def handle_blog(reply: Message, link_info, lang) -> None:
    await reply.edit_text(t("telegram.links.unsupported", lang))

