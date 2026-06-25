from __future__ import annotations

from pyrogram import filters
from pyrogram.types import Message, CallbackQuery
from pyrogram.enums import ChatType
from src.telegram import tgApp as app

from src.telegram.helpers.wrappers.adm import admin_exists, admin_only, owner_only
from src.utils.db import add_admin, remove_admin, get_all_admins, get_admin, set_admin_language, get_language, unset_altamino_id
from src.utils.i18n import t, get_langs_list
from src.telegram.helpers.keyboards.language import language_keyboard
from src.telegram.helpers.keyboards.me import me_keyboard

def _parse_target(message: Message) -> tuple[int | None, str]:
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
        return user.id, user.mention

    if len(message.command) > 1:
        arg = message.command[1]
        if arg.lstrip("-").isdigit():
            uid = int(arg)
            return uid, f"`{uid}`"

    return None, ""

def _user_link(user_id: int, name: str) -> str:
    return f"[{name}](tg://user?id={user_id})"


def _fmt_admin_row(row: dict) -> str:
    name = f"@{row['username']}" if row["username"] else str(row["user_id"])
    link = _user_link(row["user_id"], name)
    return f"  • {link} | `{row['user_id']}`\n"


@app.on_message(filters.command("admin_add"))
@owner_only
async def add_admin_handler(_, message: Message):
    lang = get_language(message.from_user.id)
    target_id, target_name = _parse_target(message)

    if target_id is None:
        await message.reply(t("telegram.adm.add.usage", lang))
        return

    if admin_exists(target_id):
        await message.reply(t("telegram.adm.add.exists", lang).format(target_name=target_name))
        return

    username: str | None = None
    if message.reply_to_message and message.reply_to_message.from_user:
        username = message.reply_to_message.from_user.username

    add_admin(user_id=target_id, added_by=message.from_user.id, username=username)
    await message.reply(t("telegram.adm.add.added", lang).format(target_name=target_name))



@app.on_message(filters.command("admin_remove"))
@owner_only
async def remove_admin_handler(_, message: Message):
    lang = get_language(message.from_user.id)
    target_id, target_name = _parse_target(message)

    if target_id is None:
        await message.reply(t("telegram.adm.remove.usage", lang))
        return

    if not admin_exists(target_id):
        await message.reply(t("telegram.adm.remove.not_exists", lang).format(target_name=target_name))
        return

    remove_admin(target_id)
    await message.reply(t("telegram.adm.remove.removed", lang).format(target_name=target_name))




@app.on_message(filters.command("admins"))
@admin_only
async def list_admins_handler(_, message: Message):
    rows = get_all_admins()

    lines = ["🛡 **Admins:**"]

    if rows:
        for row in rows:
            lines.append(_fmt_admin_row(dict(row)))
    else:
        lines.append(" _(empty)_")

    await message.reply("\n".join(lines), disable_web_page_preview=True)



@app.on_message(filters.command("setlang"))
@admin_only
async def set_language_handler(_, message: Message):
    lang = get_language(message.from_user.id)
    user_id = message.from_user.id
    langs = get_langs_list()

    if len(message.command) > 1:
        code = message.command[1].lower()
        if code not in langs:
            _langs = ", ".join(f"`{c}`" for c in langs)
            await message.reply(t("telegram.adm.langs.unknown", lang).format(langs=_langs))
            return
        set_admin_language(user_id, code)
        await message.reply(f"{t('telegram.adm.langs.set', code)} {t('lang', code)}")
        return

    await message.reply(
        t("telegram.adm.langs.btn_select", lang),
        reply_markup=language_keyboard(),
    )


@app.on_message(filters.command("me"))
@admin_only
async def me_handler(_, message: Message):
    lang = get_language(message.from_user.id)
    row = get_admin(message.from_user.id)

    if row:
        row = dict(row)
        name = f"@{row['username']}" if row["username"] else str(row["user_id"])
        link = _user_link(row["user_id"], name)
        text = f"**{link}**\nLanguage: {row.get('language', 'en')}\nAltAmino: {'✅' if row.get('altamino_id') else '❌'}"
    else:
        row={}
        text = " _(empty)_"

    await message.reply(
        text,
        reply_markup=await me_keyboard(lang, row.get('altamino_id') is not None, message.chat.type == ChatType.PRIVATE ),
        disable_web_page_preview=True
    )




@app.on_callback_query(filters.regex(r"^setlang:(.+)"))
@admin_only
async def set_language_callback(_, callback_query: CallbackQuery):
    code = str(callback_query.data).split(":")[1]
    user_id = callback_query.from_user.id
    
    langs = get_langs_list()
    
    if code not in langs:
        _langs = ", ".join(f"`{c}`" for c in langs)
        current_lang = get_language(user_id)
        await callback_query.answer(
            t("telegram.adm.langs.unknown", current_lang).format(lang=_langs), 
            show_alert=True
        )
        return

    set_admin_language(user_id, code)
    
    success_text = f"{t('telegram.adm.langs.set', code)} {t('lang', code)}"
 
    await callback_query.edit_message_text(
        text=success_text
    )
    
    await callback_query.answer(success_text)




@app.on_callback_query(filters.regex(r"changeLang"))
@admin_only
async def set_language_main_callback(_, callback_query: CallbackQuery):
    lang = get_language(callback_query.from_user.id)
    await callback_query.message.reply(
        t("telegram.adm.langs.btn_select", lang),
        reply_markup=language_keyboard(),
    )


@app.on_callback_query(filters.regex(r"unsetAltAmino"))
@admin_only
async def unsetAltAminoCallback(_, callback_query: CallbackQuery):
    unset_altamino_id(callback_query.from_user.id)
    await callback_query.message.reply(
        "✅OK",
        reply_markup=language_keyboard(),
    )


@app.on_callback_query(filters.regex(r"setAltAmino"))
@admin_only
async def setAltAminoCallback(_, callback_query: CallbackQuery):
    await on_set_altaminoid(callback_query)






async def on_set_altaminoid(msg: Message | CallbackQuery):
    lang = get_language(msg.from_user.id)
    if isinstance(msg, Message):
        await msg.reply(t("unsupported", lang))
    else:
        await msg.message.reply(t("unsupported", lang))