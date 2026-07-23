from datetime import datetime, timezone

from src.aa import client
from src.utils import reply
from altamino import respObject, args
from src.utils.i18n import t
from src.utils.wrappers.chat_settings import commands_enable_required


@client.command(["/invite"])
@commands_enable_required()
async def on_ping(event: respObject.Event):
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
            
    elif info.objectType == args.ObjectType.Community:
        await client.join_community(info.objectId)
    else:
        await reply(event, t("errors.bad_url", comId=event.comId))
        return

    await reply(event, t("ok", comId=event.comId))