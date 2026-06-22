from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.config import BOT_URL
from src.utils.i18n import t


def me_keyboard(lang: str, hasAltAminoId: bool, isPrivate: bool) -> InlineKeyboardMarkup:
    buttons = []
    
    buttons.append([InlineKeyboardButton(t("telegram.adm.langs.change", lang), callback_data=f"changeLang")])


    if hasAltAminoId:
        buttons.append([InlineKeyboardButton(t("telegram.altamino.remove", lang), callback_data=f"unsetAltAmino")])
    else:
        if isPrivate:
            buttons.append([InlineKeyboardButton(t("telegram.altamino.set", lang), callback_data=f"setAltAmino")])
        else:
            buttons.append([InlineKeyboardButton(t("telegram.altamino.set", lang), url=f"{BOT_URL}?start=setAltAmino")])
        
    return InlineKeyboardMarkup(buttons)