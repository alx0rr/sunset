
from src.altamino import client
from altamino import respObject

@client.command(["/ping"])
async def on_ping(event: respObject.Event):
    print(event.message)