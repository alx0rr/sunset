from pyrogram import filters
from pyrogram.types import Message

from src.utils.i18n import t
from src.utils.db import get_language
from src.telegram.helpers.wrappers.adm import admin_only
from src.telegram import tgApp as app
from src.utils.link_validator import extract_url, is_altamino_link
from src import altAminoClient as client

from altamino import args


async def handle_blog(reply: Message, link_info, lang) -> None:
    await reply.edit_text(t("telegram.links.unsupported", lang))


async def handle_chat(reply: Message, link_info, lang) -> None:
    await reply.edit_text(t("telegram.links.unsupported", lang))


async def handle_community(reply: Message, link_info, lang) -> None:
    await reply.edit_text(t("telegram.links.unsupported", lang))


async def handle_profile(reply: Message, link_info, lang) -> None:
    await reply.edit_text(t("telegram.links.unsupported", lang))


async def handle_wiki(reply: Message, link_info, lang) -> None:
    await reply.edit_text(t("telegram.links.unsupported", lang))





OBJECT_TYPE_HANDLERS = {
    args.ObjectType.Blog: handle_blog,
    args.ObjectType.Chat: handle_chat,
    args.ObjectType.Community: handle_community,
    args.ObjectType.Profile: handle_profile,
    args.ObjectType.Wiki: handle_wiki,
}


@app.on_message(filters.command("mod"))
@admin_only
async def link_moderation_handler(_, message: Message):
    lang = get_language(message.from_user.id)
    url = extract_url(message.text)
    reply = await message.reply(t("telegram.links.processing", lang))

    if url is None:
        await reply.edit_text(t("telegram.links.usage", lang))
        return

    if not is_altamino_link(url):
        await reply.edit_text(t("telegram.links.invalid", lang))
        return

    try:
        link_info = await client.get_from_link(url)
    except Exception as e:
        await reply.edit_text(str(e))
        return

    handler = OBJECT_TYPE_HANDLERS.get(link_info.objectType)

    if handler is None:
        await reply.edit_text(t("telegram.links.unsupported", lang))
        return

    await handler(reply, link_info, lang)