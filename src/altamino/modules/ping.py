
from src.altamino import client
from src.utils import ping_text
from altamino import respObject

@client.command(["/ping"])
async def on_ping(event: respObject.Event):
    text = "[BC]🏓Pong!\n\n"+ping_text().replace('`', "")
    if event.sub_client:
        await event.sub_client.send_message(event.message.chatId, text, event.message.messageId)
        return
    await client.send_message(event.message.chatId, text, event.message.messageId)