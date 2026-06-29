from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src import tgApp as app
from src.utils.i18n import t


async def me_keyboard(lang: str) -> InlineKeyboardMarkup:
    buttons = []
    
    buttons.append([InlineKeyboardButton(t("telegram.adm.langs.change", lang), callback_data=f"changeLang")])
    return InlineKeyboardMarkup(buttons)