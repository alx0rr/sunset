from src.aa import client
from src.utils.i18n import t
from src.utils.wrappers.admin_only import require_chat_staff, require_local_staff
from src.utils.db import ChatSettings, CommunitySettings, GreetingType
from src.utils.cache.community import apply_community_settings
from src.utils.cache.chat import apply_chat_settings
from src.utils.cmd import _args, _parse_bool
from src.utils import reply

from altamino import respObject
from altamino.objects.resp import Community


@client.command(["/chat-settings"])
@require_chat_staff
async def on_chat_settings(event: respObject.Event):
    info = await event.state.get("chat")
    if not info:
        await reply(event, t("errors.no_data", comId=event.comId))
        return

    chat: respObject.Chat = info["info"]
    s: ChatSettings = info["settings"]

    text = t("chat.settings", comId=event.comId).format(
        name=chat.title,
        members=chat.membersCount,
        greeting=t(f"common.{'on' if s.greeting_enabled else 'off'}", comId=event.comId),
        greeting_type=s.greeting_type.value,
        farewell=t(f"common.{'on' if s.farewell_enabled else 'off'}", comId=event.comId),
        commands=t(f"common.{'on' if s.commands_enabled else 'off'}", comId=event.comId),
    )
    await reply(event, text)


@client.command(["/com-settings"])
@require_local_staff
async def on_com_settings(event: respObject.Event):
    info = await event.state.get("community")
    if not info:
        await reply(event, t("errors.no_data", comId=event.comId))
        return

    community: Community = info["info"]
    s: CommunitySettings = info["settings"]

    text = t("community.settings", comId=event.comId).format(
        name=community.name,
        members=community.usersCount,
        heat=community.heat,
        language=community.primaryLanguage,
        welcome=t(f"common.{'on' if s.welcome_enabled else 'off'}", comId=event.comId),
    )
    await reply(event, text)


#chats

@client.command(["/greeting-image-on"])
@require_chat_staff
async def cmd_greeting_image_on(event: respObject.Event):
    await apply_chat_settings(
        event, greeting_type=GreetingType.IMAGE
    )
    await reply(event, t("ok.greeting_image_on", comId=event.comId))


@client.command(["/greeting-text-on"])
@require_chat_staff
async def cmd_greeting_text_on(event: respObject.Event):
    await apply_chat_settings(
        event, greeting_type=GreetingType.TEXT
    )
    await reply(event, t("ok.greeting_text_on", comId=event.comId))


@client.command(["/greeting-text"])
@require_chat_staff
async def cmd_greeting_text(event: respObject.Event):
    await apply_chat_settings(
        event, greeting_text=event.message.content
    )
    await reply(event, t("ok.greeting_text", comId=event.comId))


@client.command(["/greeting"])
@require_chat_staff
async def cmd_greeting(event: respObject.Event):
    val = _parse_bool(event.message.content)
    if val is None:
        await reply(event, t("errors.bad_bool", comId=event.comId))
        return

    await apply_chat_settings(event, greeting_enabled=val)
    await reply(event, t(f"ok.greeting_{'on' if val else 'off'}", comId=event.comId))






@client.command(["/farewell-text"])
@require_chat_staff
async def cmd_farewell_text(event: respObject.Event):
    await apply_chat_settings(event, farewell_text=event.message.content)
    await reply(event, t("ok.farewell_text", comId=event.comId))


@client.command(["/farewell"])
@require_chat_staff
async def cmd_farewell(event: respObject.Event):
    val = _parse_bool(event.message.content)
    if val is None:
        await reply(event, t("errors.bad_bool", comId=event.comId))
        return

    await apply_chat_settings(event, farewell_enabled=val)
    await reply(event, t(f"ok.farewell_{'on' if val else 'off'}", comId=event.comId))


@client.command(["/commands"])
@require_chat_staff
async def cmd_commands(event: respObject.Event):
    val = _parse_bool(event.message.content)
    if val is None:
        await reply(event, t("help", comId=event.comId))
        return

    await apply_chat_settings(event, commands_enabled=val)
    await reply(event, t(f"ok.commands_{'on' if val else 'off'}", comId=event.comId))



#communities

@client.command(["/com-welcome-text"])
@require_local_staff
async def cmd_com_welcome_text(event: respObject.Event):
    if event.comId is None:
        return

    if not event.message.content:
        await reply(event, t("errors.empty_text", comId=event.comId))
        return

    await apply_community_settings(event, welcome_text=event.message.content)
    await reply(event, t("ok.welcome_text", comId=event.comId))


@client.command(["/com-welcome"])
@require_local_staff
async def cmd_com_welcome(event: respObject.Event):
    if event.comId is None:
        return

    val = _parse_bool(event.message.content)
    if val is None:
        await reply(event, t("errors.bad_bool", comId=event.comId))
        return

    await apply_community_settings(event, welcome_enabled=val)
    await reply(event, t(f"ok.welcome_{'on' if val else 'off'}", comId=event.comId))