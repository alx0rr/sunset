from src.aa import client
from src.utils import reply
from altamino import respObject
from src.utils.i18n import t

from src.utils.wrappers.chat_settings import commands_enable_required
import random

@client.command(["/roll", "/кости"])
@commands_enable_required()
async def cmd_roll(event: respObject.Event):
    a, b = random.randint(1, 6), random.randint(1, 6)
    await reply(event, t("games.roll", comId=event.comId).format(
        nick=event.message.author.nickname, a=a, b=b, total=a + b
    ), mentionUserIds=[event.message.author.userId])

@client.command(["/who", "/кто"])
@commands_enable_required()
async def cmd_who(event: respObject.Event):
    chat = await event.state.get("chat")
    if not chat:
        return

    members = chat["info"].membersSummary
    if not members:
        return

    question = event.message.content
    pick = random.choice(members)
    await reply(event, t("games.who", comId=event.comId).format(
        question=question, nick=pick.nickname
    ), mentionUserIds=[pick.userId])



_guess_games: dict[tuple, dict] = {}

@client.command(["/guess"])
@commands_enable_required()
async def cmd_guess(event: respObject.Event):
    key = (event.comId, event.message.chatId)
    arg = event.message.content

    game = _guess_games.get(key)
    if not game:
        _guess_games[key] = {"number": random.randint(1, 100), "tries": 0}
        await reply(event, t("games.guess_start", comId=event.comId))
        return

    if not arg.isdigit():
        await reply(event, t("games.guess_need_number", comId=event.comId))
        return

    n = int(arg)
    game["tries"] += 1

    if n == game["number"]:
        del _guess_games[key]
        await reply(event, t("games.guess_win", comId=event.comId).format(
            nick=event.message.author.nickname, tries=game["tries"]
        ), mentionUserIds=[event.message.author.userId])
    else:
        key_ = "games.guess_higher" if n < game["number"] else "games.guess_lower"
        await reply(event, t(key_, comId=event.comId))