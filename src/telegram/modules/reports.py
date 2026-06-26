from __future__ import annotations

from pyrogram import filters
from pyrogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    InputMediaPhoto,
)

from src.telegram import tgApp as app
from src.telegram.helpers.wrappers import private_only
from src.telegram.helpers.wrappers.adm import admin_only
from src.utils.db import (
    create_report, add_report_photo,
    get_open_reports, count_open_reports, close_report,
    get_report, get_report_photos,
    get_language,
)
from src.utils.i18n import t
from src.utils.fsm import get_state, set_state, update_data, get_data, clear

ADMIN_LANG = "en"
LIST_LIMIT = 5


class RS:
    text   = "report:text"
    photos = "report:photos"


RS_ALL = {RS.text, RS.photos}


async def _in_report_state(_, __, message: Message) -> bool:
    return get_state(message.from_user.id) in RS_ALL


in_report_state = filters.create(_in_report_state)



def _submit_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(t("telegram.reports.btn_send",   lang), callback_data="report:submit"),
        InlineKeyboardButton(t("telegram.reports.btn_cancel", lang), callback_data="report:cancel"),
    ]])


def _report_keyboard(report_id: int, user_id: int, lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(t("telegram.reports.btn_write", lang), url=f"tg://user?id={user_id}"),
        InlineKeyboardButton(t("telegram.reports.btn_close", lang), callback_data=f"report:close:{report_id}"),
    ]])


def _list_keyboard(reports: list, offset: int, total: int) -> InlineKeyboardMarkup | None:
    rows = []

    for r in reports:
        name = f"@{r['username']}" if r["username"] else str(r["user_id"])
        rows.append([InlineKeyboardButton(
            f"#{r['id']} — {name}",
            callback_data=f"report:view:{r['id']}",
        )])

    nav = []
    if offset > 0:
        nav.append(InlineKeyboardButton("◀️", callback_data=f"report:list:{offset - LIST_LIMIT}"))
    if offset + LIST_LIMIT < total:
        nav.append(InlineKeyboardButton("▶️", callback_data=f"report:list:{offset + LIST_LIMIT}"))
    if nav:
        rows.append(nav)

    return InlineKeyboardMarkup(rows) if rows else None



def _report_card(report_id: int, user_id: int, username: str | None, text: str | None, lang: str) -> str:
    name = f"@{username}" if username else str(user_id)
    return t("telegram.reports.card", lang).format(
        id=report_id,
        name=name,
        user_id=user_id,
        text=text or "—",
    )

async def _edit_or_reply(target: Message | CallbackQuery, text: str, keyboard=None) -> None:
    if isinstance(target, CallbackQuery):
        await target.edit_message_text(text, reply_markup=keyboard)
    else:
        await target.reply(text, reply_markup=keyboard)



@app.on_message(filters.command("report") & filters.private)
@private_only
async def report_handler(_, message: Message):
    user_id = message.from_user.id
    lang = get_language(user_id)
    clear(user_id)
    set_state(user_id, RS.text)
    update_data(user_id, photos=[], text=None)
    await message.reply(t("telegram.reports.ask_text", lang))


@app.on_message(filters.private & in_report_state & ~filters.command(""))
async def report_input_handler(_, message: Message):
    user_id = message.from_user.id
    state = get_state(user_id)
    lang = get_language(user_id)

    if state == RS.text:
        if not message.text and not message.caption and not message.photo:
            await message.reply(t("telegram.reports.ask_text", lang))
            return

        text = (message.text or message.caption or "").strip() or None
        update_data(user_id, text=text)
        set_state(user_id, RS.photos)

        if message.photo:
            photos: list = get_data(user_id).get("photos", [])
            photos.append(message.photo.file_id)
            update_data(user_id, photos=photos)

        await message.reply(
            t("telegram.reports.ask_photos", lang),
            reply_markup=_submit_keyboard(lang),
        )

    elif state == RS.photos:
        if message.photo:
            photos = get_data(user_id).get("photos", [])
            photos.append(message.photo.file_id)
            update_data(user_id, photos=photos)
            await message.reply(
                t("telegram.reports.photo_added", lang).format(n=len(photos)),
                reply_markup=_submit_keyboard(lang),
            )
        else:
            await message.reply(
                t("telegram.reports.only_photos", lang),
                reply_markup=_submit_keyboard(lang),
            )


@app.on_callback_query(filters.regex(r"^report:submit$"))
async def report_submit_callback(_, query: CallbackQuery):
    user_id = query.from_user.id
    lang = get_language(user_id)

    if get_state(user_id) != RS.photos:
        await query.answer()
        return

    data = get_data(user_id)
    text: str | None = data.get("text")
    photos: list[str] = data.get("photos", [])
    clear(user_id)

    report_id = create_report(user_id=user_id, username=query.from_user.username, text=text)
    for file_id in photos:
        add_report_photo(report_id, file_id)

    await query.edit_message_text(t("telegram.reports.sent", lang).format(id=report_id))
    await query.answer()


@app.on_callback_query(filters.regex(r"^report:cancel$"))
async def report_cancel_callback(_, query: CallbackQuery):
    user_id = query.from_user.id
    lang = get_language(user_id)
    clear(user_id)
    await query.edit_message_text(t("telegram.reports.cancelled", lang))
    await query.answer()


@app.on_message(filters.command("check_reports"))
@admin_only
async def check_reports_handler(_, message: Message):
    lang = get_language(message.from_user.id)
    await _send_report_list(message, lang, offset=0)


async def _send_report_list(target: Message | CallbackQuery, lang: str, offset: int = 0) -> None:
    reports = get_open_reports(limit=LIST_LIMIT, offset=offset)
    total = count_open_reports()

    if not reports:
        await _edit_or_reply(target, t("telegram.reports.empty", lang))
        return

    text = t("telegram.reports.list_header", lang).format(total=total)
    keyboard = _list_keyboard(reports, offset, total)
    await _edit_or_reply(target, text, keyboard)


@app.on_callback_query(filters.regex(r"^report:list:(\d+)$"))
@admin_only
async def report_list_page_callback(_, query: CallbackQuery):
    offset = int(query.data.split(":")[2])
    lang = get_language(query.from_user.id)
    await _send_report_list(query, lang, offset=offset)
    await query.answer()


@app.on_callback_query(filters.regex(r"^report:view:(\d+)$"))
@admin_only
async def report_view_callback(_, query: CallbackQuery):
    report_id = int(query.data.split(":")[2])
    lang = get_language(query.from_user.id)
    row = get_report(report_id)

    if not row:
        await query.answer(t("telegram.reports.not_found", lang), show_alert=True)
        return

    photos = get_report_photos(report_id)
    card = _report_card(report_id, row["user_id"], row["username"], row["text"], lang)
    keyboard = _report_keyboard(report_id, row["user_id"], lang)

    await query.answer()

    if photos:
        media = [
            InputMediaPhoto(file_id, caption=card if i == 0 else "")
            for i, file_id in enumerate(photos)
        ]
        await query.message.reply_media_group(media)
        await query.message.reply(card, reply_markup=keyboard)
    else:
        await query.edit_message_text(card, reply_markup=keyboard)

@app.on_callback_query(filters.regex(r"^report:close:(\d+)$"))
@admin_only
async def report_close_callback(_, query: CallbackQuery):
    report_id = int(query.data.split(":")[2])
    lang = get_language(query.from_user.id)
    close_report(report_id)
    await query.edit_message_text(t("telegram.reports.closed", lang).format(id=report_id))
    await query.answer()