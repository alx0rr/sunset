from pyrogram.types import Message

from src.utils.i18n import t

from altamino.objects.resp.from_code import FromCode
from src import altAminoClient as client
from altamino import AsyncSubClient

async def handle_community(reply: Message, link_info: FromCode, lang) -> None:
    client.set_language(lang)
    print(link_info.comId)
    sub= AsyncSubClient(client, link_info.comId)