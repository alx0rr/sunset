from datetime import datetime, timezone

from src.aa import client
from src.utils.i18n import t
from src.utils.greeting_image import make_greeting_image
from src.utils import reply, safe_format
from src.utils.db import ChatSettings, get_chat_settings, get_community_settings, GreetingType
from src import community_cache, chat_cache
from src.utils.wrappers.chat_settings import ignore_yourself
from altamino import respObject, args, AsyncClient, AsyncSubClient

@client.middleware(args.wsEvent.ANY)
async def cache(data: respObject.Event):
    comId = data.comId
    if comId in (0, "g"): comId = 0; data.comId = 0
    chatId = data.message.chatId
    chat = None
    community = None

    c = data.client if not comId else data.sub_client

    if comId:
        community = community_cache.get(comId)
        if community is None:
            community = {
                "info": await client.get_community_info(comId),
                "settings": await get_community_settings(comId)
            }
            community_cache.set(comId, community)

    if chatId:
        chat = chat_cache.get((comId, chatId))
        if chat is None:
            chat = {
                "info": await c.get_chat(chatId),
                "settings": await get_chat_settings(comId, chatId)
            }
            chat_cache.set((comId, chatId), chat)

    await data.state.set("chat", chat)
    await data.state.set("community", community)



@client.event(args.wsEvent.on_group_member_join)
@ignore_yourself()
async def on_join(event: respObject.Event):
    chat = await event.state.get("chat")
    if not chat:
        return

    settings: ChatSettings = chat["settings"]
    info: respObject.Chat = chat["info"]

    if not settings.greeting_enabled:
        return

    author = event.message.author
    fmt = dict(
        nick=author.nickname,
        title=info.title,
        members=info.membersCount,
    )

    if settings.greeting_type == GreetingType.IMAGE:
        target:  AsyncSubClient | AsyncClient = event.sub_client or event.client
        tpl = t("common.greeting_text_image", comId=event.comId)
        text = safe_format(tpl, **fmt)
        file = await make_greeting_image(text, author.icon)
        await target.send_media(event.message.chatId, file)
        return

    tpl = settings.greeting_text or t("common.greeting_text", comId=event.comId)
    await reply(event, safe_format(tpl, **fmt), [author.userId], reply=False)


@client.event(args.wsEvent.on_group_member_leave)
@ignore_yourself()
async def on_leave(event: respObject.Event):
    chat = await event.state.get("chat")
    if not chat:
        return

    settings: ChatSettings = chat["settings"]
    info: respObject.Chat = chat["info"]

    if not settings.farewell_enabled:
        return

    author = event.message.author
    tpl = settings.farewell_text or t("common.farewell_text", comId=event.comId)

    text = safe_format(
        tpl,
        nick=author.nickname,
        title=info.title,
        members=info.membersCount,
    )
    await reply(event, text, [author.userId], reply=False)

@client.event(args.wsEvent.on_chat_invite)
async def on_invite(event: respObject.Event):
    c = event.sub_client or event.client
    await c.join_chat(event.message.chatId)