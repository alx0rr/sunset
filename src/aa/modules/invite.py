from datetime import datetime, timezone

from src.aa import client
from src.utils import reply
from altamino import respObject, args
from src.utils.i18n import t
from src.utils.wrappers.chat_settings import commands_enable_required





@client.command(["/leave"])
@commands_enable_required()
async def on_leave(event: respObject.Event):
    c = event.sub_client or event.client
    await c.leave_chat(event.message.chatId)

@client.command(["/invite"])
@commands_enable_required()
async def on_invite(event: respObject.Event):
    if event.message.content is None:
        await reply(event, t("errors.bad_url", comId=event.comId))
        return
    try:
        info: respObject.FromCode = await client.get_from_link(event.message.content)
    except:
        await reply(event, t("errors.bad_url", comId=event.comId))
        return


    if info.objectType == args.ObjectType.Chat:
        if info.comId not in ("g", 0, event.comId, None):
            await reply(event, t("errors.another_community", comId=event.comId))
            return
        c = event.sub_client or event.client
        await c.join_chat(info.objectId)
        await c.send_message(info.objectId, t(f"on_chat_invite", comId=event.comId))
            
    elif info.objectType == args.ObjectType.Community:
        await client.join_community(info.objectId)
    else:
        await reply(event, t("errors.bad_url", comId=event.comId))
        return

    await reply(event, t("ok.done", comId=event.comId))