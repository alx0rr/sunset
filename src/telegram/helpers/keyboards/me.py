from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src import tgApp as app
from src.utils.i18n import t


async def me_keyboard(lang: str, hasAltAminoId: bool, isPrivate: bool) -> InlineKeyboardMarkup:
    buttons = []
    
    buttons.append([InlineKeyboardButton(t("telegram.adm.langs.change", lang), callback_data=f"changeLang")])


    if hasAltAminoId:
        buttons.append([InlineKeyboardButton(t("telegram.altamino.remove", lang), callback_data=f"unsetAltAmino")])
    else:
        if isPrivate:
            buttons.append([InlineKeyboardButton(t("telegram.altamino.set", lang), callback_data=f"setAltAmino")])
        else:
            me = await app.get_me()
            buttons.append([InlineKeyboardButton(t("telegram.altamino.set", lang), url=f"https://t.me/{me.username}?start=setAltAmino")])
        
    return InlineKeyboardMarkup(buttons)