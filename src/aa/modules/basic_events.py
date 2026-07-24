from datetime import datetime, timezone

from src.aa import client
from src.utils.i18n import t
from src.utils.roles import UserRole
from src.utils.greeting_image import make_greeting_image
from src.utils import reply, safe_format
from src.utils.db import ChatSettings, get_chat_settings, get_community_settings, GreetingType
from src import community_cache, chat_cache
from src.utils.wrappers.chat_settings import ignore_yourself, chat_type_required
from altamino import respObject, args, AsyncClient, AsyncSubClient
from src.config import DEV_USERS, DEV_MODE, FLOOD_LIMIT, FLOOD_WINDOW, IGNORE_TIME
from time import monotonic


_msg_times: dict[tuple, list[float]] = {}
_ignored: dict[tuple, float] = {} 


def _key(data) -> tuple:
    return (data.message.author.userId, data.message.chatId)


def _check_flood(key: tuple) -> bool:
    now = monotonic()

    until = _ignored.get(key)
    if until is not None:
        if now < until:
            return True
        del _ignored[key]

    times = _msg_times.setdefault(key, [])
    times[:] = [t for t in times if now - t < FLOOD_WINDOW]
    times.append(now)

    if len(times) > FLOOD_LIMIT:
        _ignored[key] = now + IGNORE_TIME
        times.clear()
        return True

    return False




@client.middleware(args.wsEvent.ANY)
async def dev_mode(data: respObject.Event):
	if DEV_MODE and DEV_USERS:
		if data.message.author.userId not in DEV_USERS + [client.userId]:
			return False


@client.middleware(args.wsEvent.chat_message)
@ignore_yourself()
async def antiflood(data: respObject.Event):

    role = getattr(data.message.author, "role", 0)
    if UserRole.is_privileged_role(role):
        return

    key = _key(data)
    was_ignored = key in _ignored

    if _check_flood(key):
        if not was_ignored:
            await reply(data, t("errors.flood", comId=data.comId))
        return False

    return


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
@chat_type_required([args.ChatTypes.Public, args.ChatTypes.Group])
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
@chat_type_required([args.ChatTypes.Public, args.ChatTypes.Group])
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
	await c.send_message(event.message.chatId, t(f"on_chat_invite", comId=event.comId))