from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.utils.i18n import t, get_langs_list



def language_keyboard() -> InlineKeyboardMarkup:
    langs = get_langs_list()
    buttons = []
    
    for code in langs:
        text = t("lang", code)
        buttons.append([InlineKeyboardButton(text, callback_data=f"setlang:{code}")])
        
    return InlineKeyboardMarkup(buttons)