from altamino import args
from pyrogram import filters
from pyrogram.types import Message

from src import altAminoClient as client
from src.telegram import tgApp as app
from src.telegram.helpers.wrappers import private_only
from src.telegram.helpers.wrappers.adm import admin_only
from src.telegram.modules.chats import handle_chat
from src.telegram.modules.mod_community import handle_community
from src.telegram.modules.posts import handle_blog, handle_wiki
from src.telegram.modules.users import handle_profile
from src.utils.db import get_language
from src.utils.i18n import t
from src.utils.link_validator import extract_url, is_altamino_link

OBJECT_TYPE_HANDLERS = {
    args.ObjectType.Blog: handle_blog,
    args.ObjectType.Chat: handle_chat,
    args.ObjectType.Community: handle_community,
    args.ObjectType.Profile: handle_profile,
    args.ObjectType.Wiki: handle_wiki,
}


@app.on_message(filters.command("mod"))
@private_only
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
        client.set_language(lang)
        link_info = await client.get_from_link(url)
    except Exception as e:
        await reply.edit_text(str(e))
        return

    handler = OBJECT_TYPE_HANDLERS.get(
        link_info.objectType if link_info.objectType is not None else -1000
    )

    if handler is None:
        await reply.edit_text(t("telegram.links.unsupported", lang))
        return

    await handler(reply, link_info, lang)
