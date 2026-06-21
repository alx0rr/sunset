from datetime import datetime, timezone

from src.altamino import client
from src.utils import ping_text
from altamino import respObject


@client.command(["/ping"])
async def on_ping(event: respObject.Event):
    created = datetime.fromisoformat(event.message.createdTime.replace("Z", "+00:00"))
    latency_ms = (datetime.now(timezone.utc) - created).total_seconds() * 1000

    text = "[BC]🏓Pong!\n\n" + ping_text(latency_ms).replace('`', "")

    if event.sub_client:
        await event.sub_client.send_message(event.message.chatId, text, event.message.messageId)
        return
    await client.send_message(event.message.chatId, text, event.message.messageId)