from __future__ import annotations

from pyrogram import filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from src import altAminoClient as client
from altamino import AsyncSubClient
from src.telegram import tgApp as app
from src.telegram.helpers.wrappers.adm import admin_only
from src.telegram.helpers.wrappers import private_only
from src.utils.db import get_language
from src.utils.i18n import t
from src.utils.fsm import get_state, set_state, get_data, update_data, clear


# ---------------------------------------------------------------------------
# States
# ---------------------------------------------------------------------------

class CC:
    name    = "cc:name"
    aminoid = "cc:aminoid"
    agent   = "cc:agent"
    editing = "cc:editing"

    ALL = {name, aminoid, agent, editing}


# ---------------------------------------------------------------------------
# Custom filter: пользователь в активном CC-состоянии
# ---------------------------------------------------------------------------

async def _in_cc_state(_, __, message: Message) -> bool:
    return get_state(message.from_user.id) in CC.ALL

in_cc_state = filters.create(_in_cc_state)


# ---------------------------------------------------------------------------
# Keyboards
# ---------------------------------------------------------------------------

def _preview_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t("telegram.community.create.btn_edit_name",    lang), callback_data="cc:edit:name"),
            InlineKeyboardButton(t("telegram.community.create.btn_edit_aminoid", lang), callback_data="cc:edit:aminoid"),
            InlineKeyboardButton(t("telegram.community.create.btn_edit_agent",   lang), callback_data="cc:edit:agent"),
        ],
        [
            InlineKeyboardButton(t("telegram.community.create.btn_create", lang), callback_data="cc:confirm"),
            InlineKeyboardButton(t("telegram.community.create.btn_cancel", lang), callback_data="cc:cancel"),
        ],
    ])


def _error_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t("telegram.community.create.btn_edit_name",    lang), callback_data="cc:edit:name"),
            InlineKeyboardButton(t("telegram.community.create.btn_edit_aminoid", lang), callback_data="cc:edit:aminoid"),
            InlineKeyboardButton(t("telegram.community.create.btn_edit_agent",   lang), callback_data="cc:edit:agent"),
        ],
        [InlineKeyboardButton(t("telegram.community.create.btn_cancel", lang), callback_data="cc:cancel")],
    ])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FIELD_LABELS = {
    "name":    "telegram.community.create.btn_edit_name",
    "aminoid": "telegram.community.create.btn_edit_aminoid",
    "agent":   "telegram.community.create.btn_edit_agent",
}

def _preview_text(data: dict, lang: str) -> str:
    return t("telegram.community.create.preview", lang).format(
        name=data.get("name", "—"),
        aminoid=data.get("aminoid", "—"),
        agent=data.get("agent", "—"),
    )


# ---------------------------------------------------------------------------
# /create_community — entry point
# ---------------------------------------------------------------------------

@app.on_message(filters.command("create_community"))
@admin_only
@private_only
async def create_community_handler(_, message: Message):
    user_id = message.from_user.id
    lang = get_language(user_id)
    clear(user_id)
    set_state(user_id, CC.name)

    await message.reply(t("telegram.community.create.start", lang))


# ---------------------------------------------------------------------------
# Text input — только личка + только если в активном состоянии
# ---------------------------------------------------------------------------

@app.on_message(filters.text & filters.private & in_cc_state & ~filters.command(""))
async def community_input_handler(_, message: Message):
    user_id = message.from_user.id
    state = get_state(user_id)
    lang = get_language(user_id)
    text = message.text.strip()

    if state == CC.name:
        update_data(user_id, name=text)
        set_state(user_id, CC.aminoid)
        await message.reply(t("telegram.community.create.ask_aminoid", lang))

    elif state == CC.aminoid:
        update_data(user_id, aminoid=text)
        set_state(user_id, CC.agent)
        await message.reply(t("telegram.community.create.ask_agent", lang))

    elif state == CC.agent:
        update_data(user_id, agent=text)
        set_state(user_id, None)
        data = get_data(user_id)
        await message.reply(_preview_text(data, lang), reply_markup=_preview_keyboard(lang))

    elif state == CC.editing:
        field = get_data(user_id).get("edit_field")
        if field:
            update_data(user_id, **{field: text})
        set_state(user_id, None)
        data = get_data(user_id)
        await message.reply(_preview_text(data, lang), reply_markup=_preview_keyboard(lang))


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------

@app.on_callback_query(filters.regex(r"^cc:edit:(\w+)$"))
@admin_only
async def cc_edit_callback(_, query: CallbackQuery):
    field = query.data.split(":")[2]
    if field not in FIELD_LABELS:
        await query.answer()
        return

    user_id = query.from_user.id
    lang = get_language(user_id)
    field_label = t(FIELD_LABELS[field], lang)

    update_data(user_id, edit_field=field)
    set_state(user_id, CC.editing)

    await query.edit_message_text(
        t("telegram.community.create.edit_prompt", lang).format(field=field_label)
    )
    await query.answer()


@app.on_callback_query(filters.regex(r"^cc:confirm$"))
@admin_only
async def cc_confirm_callback(_, query: CallbackQuery):
    user_id = query.from_user.id
    lang = get_language(user_id)
    data = get_data(user_id)

    name    = data.get("name", "").strip()
    aminoid = data.get("aminoid", "").strip()
    agent   = data.get("agent", "").strip()

    missing = []
    if not name:
        missing.append(t("telegram.community.create.btn_edit_name", lang))
    if not aminoid:
        missing.append(t("telegram.community.create.btn_edit_aminoid", lang))
    if not agent:
        missing.append(t("telegram.community.create.btn_edit_agent", lang))

    if missing:
        await query.answer(
            t("telegram.community.create.missing_fields", lang).format(
                fields=", ".join(missing)
            ),
            show_alert=True,
        )
        return

    await query.edit_message_text(t("telegram.community.create.creating", lang))
    await query.answer()

    try:
        sub = AsyncSubClient(client)
        sub.set_language(lang)
        await sub.create_community(name, aminoid, agent, lang)
        clear(user_id)
        await query.edit_message_text(
            t("telegram.community.create.success", lang).format(name=name)
        )
    except Exception as e:
        await query.edit_message_text(
            t("telegram.community.create.error", lang).format(error=str(e)),
            reply_markup=_error_keyboard(lang),
        )


@app.on_callback_query(filters.regex(r"^cc:cancel$"))
@admin_only
async def cc_cancel_callback(_, query: CallbackQuery):
    user_id = query.from_user.id
    lang = get_language(user_id)
    clear(user_id)
    await query.edit_message_text(t("telegram.community.create.cancelled", lang))
    await query.answer()


# ---------------------------------------------------------------------------
# Link handler
# ---------------------------------------------------------------------------

async def handle_community(reply: Message, link_info, lang) -> None:
    await reply.edit_text(t("telegram.links.unsupported", lang))