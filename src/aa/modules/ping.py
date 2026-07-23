from datetime import datetime, timezone

from src.aa import client
from src.utils import ping_text, reply
from altamino import respObject
from src.utils.i18n import t


@client.command(["/ping"])
async def on_ping(event: respObject.Event):
    created = datetime.fromisoformat(event.message.createdTime.replace("Z", "+00:00"))
    latency_ms = (datetime.now(timezone.utc) - created).total_seconds() * 1000

    text = "[BC]🏓Pong!\n\n" + ping_text(latency_ms).replace('`', "")
    await reply(event, text)


@client.command(["/help", "/commands", "/команды", "/помощь"])
async def on_ping(event: respObject.Event):
    await reply(event, t("help", comId=event.comId))