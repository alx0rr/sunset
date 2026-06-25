from __future__ import annotations

from altamino import AsyncSubClient
from altamino.objects.resp.from_code import FromCode
from pyrogram import filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from src import altAminoClient as client
from src.telegram import tgApp as app
from src.telegram.helpers.wrappers.adm import admin_only
from src.utils.db import get_language
from src.utils.i18n import t


def _community_keyboard(lang: str, com_id: str) -> InlineKeyboardMarkup:
    p = f"com:{com_id}"
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    t("telegram.community.btn_edit", lang), callback_data=f"{p}:edit"
                )
            ],
            [
                InlineKeyboardButton(
                    t("telegram.community.btn_delete", lang),
                    callback_data=f"{p}:delete",
                )
            ],
        ]
    )


def _edit_keyboard(lang: str, com_id: str) -> InlineKeyboardMarkup:
    p = f"com:{com_id}"
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    t("telegram.community.edit.btn_name", lang),
                    callback_data=f"{p}:edit:name",
                )
            ],
            [
                InlineKeyboardButton(
                    t("telegram.community.edit.btn_description", lang),
                    callback_data=f"{p}:edit:description",
                )
            ],
            [
                InlineKeyboardButton(
                    t("telegram.community.edit.btn_icon", lang),
                    callback_data=f"{p}:edit:icon",
                )
            ],
            [
                InlineKeyboardButton(
                    t("telegram.community.edit.btn_banner", lang),
                    callback_data=f"{p}:edit:banner",
                )
            ],
            [
                InlineKeyboardButton(
                    t("telegram.community.btn_back", lang), callback_data=f"{p}:back"
                )
            ],
        ]
    )


def _confirm_delete_keyboard(lang: str, com_id: str) -> InlineKeyboardMarkup:
    p = f"com:{com_id}"
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    t("telegram.community.delete.btn_confirm", lang),
                    callback_data=f"{p}:delete:confirm",
                ),
                InlineKeyboardButton(
                    t("telegram.community.delete.btn_cancel", lang),
                    callback_data=f"{p}:back",
                ),
            ]
        ]
    )


async def handle_community(reply: Message, link_info: FromCode, lang: str) -> None:
    com_id = str(link_info.comId)
    await reply.edit_text(
        t("telegram.community.panel", lang),
        reply_markup=_community_keyboard(lang, com_id),
    )

@app.on_callback_query(filters.regex(r"^comSettings:([^:]+)$"))
@admin_only
async def community_settings_callback(_, query: CallbackQuery):
    aminoid = str(query.data).split(":")[1]
    lang = get_language(query.from_user.id)
    print(aminoid)
    try:
        client.set_language(lang)
        info = await client.get_from_link(f"https://altamino.top/c/{aminoid}")
        await handle_community(query.message, info, lang)
        await query.answer()
    except Exception as e:
        await query.answer(str(e))



@app.on_callback_query(filters.regex(r"^com:([^:]+):edit$"))
@admin_only
async def community_edit_callback(_, query: CallbackQuery):
    com_id = str(query.data).split(":")[1]
    lang = get_language(query.from_user.id)
    await query.edit_message_text(
        t("telegram.community.edit.panel", lang),
        reply_markup=_edit_keyboard(lang, com_id),
    )
    await query.answer()


@app.on_callback_query(filters.regex(r"^com:([^:]+):edit:(\w+)$"))
@admin_only
async def community_edit_field_callback(_, query: CallbackQuery):
    _, com_id, field, _ = str(query.data).split(":")
    lang = get_language(query.from_user.id)
    await query.edit_message_text(t("unsupported", lang))
    await query.answer()


@app.on_callback_query(filters.regex(r"^com:([^:]+):delete$"))
@admin_only
async def community_delete_callback(_, query: CallbackQuery):
    com_id = str(query.data).split(":")[1]
    lang = get_language(query.from_user.id)
    await query.edit_message_text(
        t("telegram.community.delete.confirm", lang),
        reply_markup=_confirm_delete_keyboard(lang, com_id),
    )
    await query.answer()


@app.on_callback_query(filters.regex(r"^com:([^:]+):delete:confirm$"))
@admin_only
async def community_delete_confirm_callback(_, query: CallbackQuery):
    com_id = str(query.data).split(":")[1]
    lang = get_language(query.from_user.id)
    await query.edit_message_text(t("telegram.community.delete.deleting", lang))
    await query.answer()
    try:
        sub = AsyncSubClient(client, int(com_id))
        await sub.delete_community()
        await query.edit_message_text(t("telegram.community.delete.success", lang))
    except Exception as e:
        await query.edit_message_text(
            t("telegram.community.delete.error", lang).format(error=str(e)),
            reply_markup=_confirm_delete_keyboard(lang, com_id),
        )


@app.on_callback_query(filters.regex(r"^com:([^:]+):back$"))
@admin_only
async def community_back_callback(_, query: CallbackQuery):
    com_id = str(query.data).split(":")[1]
    lang = get_language(query.from_user.id)
    await query.edit_message_text(
        t("telegram.community.panel", lang),
        reply_markup=_community_keyboard(lang, com_id),
    )
    await query.answer()
