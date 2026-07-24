from src.aa import client
from src.utils import reply
from altamino import respObject, args
from src.utils.i18n import t

from src.utils.wrappers.chat_settings import commands_enable_required, chat_type_required
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
@chat_type_required([args.ChatTypes.Public, args.ChatTypes.Group])
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


@client.command(["/flip", "/монетка"])
@commands_enable_required()
async def cmd_coin(event: respObject.Event):
    side = random.choice(["heads", "tails"])
    await reply(event, t(f"games.coin_{side}", comId=event.comId).format(
        nick=event.message.author.nickname
    ), mentionUserIds=[event.message.author.userId])


@client.command(["/8ball", "/шар"])
@commands_enable_required()
async def cmd_8ball(event: respObject.Event):
    if not event.message.content.strip():
        await reply(event, t("games.ball_ask", comId=event.comId))
        return

    n = random.randint(0, 9)
    await reply(event, t(f"games.ball_{n}", comId=event.comId))


@client.command(["/percent", "/процент"])
@commands_enable_required()
async def cmd_percent(event: respObject.Event):
    what = event.message.content.strip()
    if not what:
        await reply(event, t("games.percent_ask", comId=event.comId))
        return

    value = random.randint(0, 100)
    await reply(event, t("games.percent", comId=event.comId).format(
        nick=event.message.author.nickname, what=what, value=value
    ), mentionUserIds=[event.message.author.userId])


@client.command(["/ship", "/шип"])
@commands_enable_required()
@chat_type_required([args.ChatTypes.Public, args.ChatTypes.Group])
async def cmd_ship(event: respObject.Event):
    chat = await event.state.get("chat")
    if not chat:
        return

    members = chat["info"].membersSummary
    if len(members) < 2:
        return

    a, b = random.sample(members, 2)
    love = random.randint(0, 100)
    await reply(event, t("games.ship", comId=event.comId).format(
        a=a.nickname, b=b.nickname, love=love
    ), mentionUserIds=[a.userId, b.userId])



_RPS = {
    "камень": 0, "rock": 0, "🪨": 0,
    "ножницы": 1, "scissors": 1, "✂️": 1,
    "бумага": 2, "paper": 2, "📄": 2,
}

@client.command(["/rps", "/кнб"])
@commands_enable_required()
async def cmd_rps(event: respObject.Event):
    choice = event.message.content.strip().lower()
    user = _RPS.get(choice)
    if user is None:
        await reply(event, t("games.rps_help", comId=event.comId))
        return

    bot = random.randint(0, 2)
    if user == bot:
        result = "draw"
    elif (user + 1) % 3 == bot:
        result = "lose"
    else:
        result = "win"

    await reply(event, t(f"games.rps_{result}", comId=event.comId).format(
        nick=event.message.author.nickname,
        user=t(f"games.rps_name_{user}", comId=event.comId),
        bot=t(f"games.rps_name_{bot}", comId=event.comId),
    ), mentionUserIds=[event.message.author.userId])


@client.command(["/dice", "/дайс"])
@commands_enable_required()
async def cmd_dice(event: respObject.Event):
    arg = event.message.content.strip()
    sides = int(arg) if arg.isdigit() and 2 <= int(arg) <= 1000 else 6
    result = random.randint(1, sides)
    await reply(event, t("games.dice", comId=event.comId).format(
        nick=event.message.author.nickname, sides=sides, result=result
    ), mentionUserIds=[event.message.author.userId])


import re

@client.command(["/choose", "/выбери"])
@commands_enable_required()
async def cmd_choose(event: respObject.Event):
    raw = event.message.content
    parts = re.split(r",|\s+(?:или|or|o|ou)\s+", raw, flags=re.IGNORECASE)
    options = [x.strip() for x in parts if x.strip()]

    if len(options) < 2:
        await reply(event, t("games.choose_help", comId=event.comId))
        return

    await reply(event, t("games.choose", comId=event.comId).format(
        pick=random.choice(options)
    ))


@client.command(["/roulette", "/рулетка"])
@commands_enable_required()
@chat_type_required([args.ChatTypes.Public, args.ChatTypes.Group])
async def cmd_roulette(event: respObject.Event):
    chat = await event.state.get("chat")
    if not chat:
        return
    members = chat["info"].membersSummary
    if not members:
        return
    victim = random.choice(members)
    survived = random.random() > 1 / 6
    key = "roulette_safe" if survived else "roulette_bang"
    await reply(event, t(f"games.{key}", comId=event.comId).format(
        nick=victim.nickname
    ), mentionUserIds=[victim.userId])