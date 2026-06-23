from __future__ import annotations

from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import filters

from altamino.objects.resp.from_code import FromCode
from altamino.objects.args.administrators_rank import AltAminoAdminRank
from altamino import AsyncSubClient
from src import altAminoClient as client
from src.telegram import tgApp as app
from src.telegram.helpers.wrappers.adm import admin_only
from src.utils.i18n import t
from src.utils.db import get_language


def _community_keyboard(lang: str, user_id: str, com_id: str) -> InlineKeyboardMarkup:
	p = f"profile:{user_id}:{com_id}"
	return InlineKeyboardMarkup([
		[
			InlineKeyboardButton(t("telegram.profile.btn_ban",      lang), callback_data=f"{p}:ban"),
			InlineKeyboardButton(t("telegram.profile.btn_unban",    lang), callback_data=f"{p}:unban"),
		],
		[
			InlineKeyboardButton(t("telegram.profile.btn_agent",    lang), callback_data=f"{p}:agent"),
			InlineKeyboardButton(t("telegram.profile.btn_leader",   lang), callback_data=f"{p}:leader"),
			InlineKeyboardButton(t("telegram.profile.btn_curator",  lang), callback_data=f"{p}:curator"),
		],
		[
			InlineKeyboardButton(t("telegram.profile.btn_unpromote", lang), callback_data=f"{p}:unpromote"),
		],
	])


def _global_keyboard(lang: str, user_id: str) -> InlineKeyboardMarkup:
	p = f"profile:{user_id}:global"
	return InlineKeyboardMarkup([
		[
			InlineKeyboardButton(t("telegram.profile.btn_ban_global",   lang), callback_data=f"{p}:ban"),
			InlineKeyboardButton(t("telegram.profile.btn_unban_global", lang), callback_data=f"{p}:unban"),
		],
	])


async def handle_profile(reply: Message, link_info: FromCode, lang: str) -> None:
	com_id  = link_info.comId
	user_id = str(link_info.objectId)

	if com_id:
		keyboard = _community_keyboard(lang, user_id, str(com_id))
		text = t("telegram.profile.panel_community", lang)
	else:
		keyboard = _global_keyboard(lang, user_id)
		text = t("telegram.profile.panel_global", lang)

	await reply.edit_text(text, reply_markup=keyboard)


@app.on_callback_query(filters.regex(r"^profile:([^:]+):([^:]+):(\w+)$"))
@admin_only
async def profile_action_callback(_, query: CallbackQuery):
	_, user_id, com_id, action = query.data.split(":")
	lang = get_language(query.from_user.id)

	await query.answer()

	is_global = com_id == "global"

	try:
		if is_global:
			await _handle_global_action(action, user_id, lang, query)
		else:
			await _handle_community_action(action, user_id, com_id, lang, query)
	except Exception as e:
		await query.message.edit_text(
			t("telegram.profile.error", lang).format(error=str(e)),
			reply_markup=query.message.reply_markup,
		)


async def _handle_community_action(
	action: str, user_id: str, com_id: str, lang: str, query: CallbackQuery
) -> None:
	sub = AsyncSubClient(client, int(com_id))
	client.set_language(lang)
	if action == "ban":
		await sub.ban_user(user_id)
		await query.message.edit_text(t("telegram.profile.banned", lang))

	elif action == "unban":
		await sub.unban_user(user_id)
		await query.message.edit_text(t("telegram.profile.unbanned", lang))

	elif action == "agent":
		await sub.promote_user(user_id, AltAminoAdminRank.Agent)
		await query.message.edit_text(t("telegram.profile.promoted_agent", lang))

	elif action == "leader":
		await sub.promote_user(user_id, AltAminoAdminRank.Leader)
		await query.message.edit_text(t("telegram.profile.promoted_leader", lang))

	elif action == "curator":
		await sub.promote_user(user_id, AltAminoAdminRank.Curator)
		await query.message.edit_text(t("telegram.profile.promoted_curator", lang))

	elif action == "unpromote":
		await sub.unpromote_user(user_id)
		await query.message.edit_text(t("telegram.profile.unpromoted", lang))


async def _handle_global_action(
	action: str, user_id: str, lang: str, query: CallbackQuery
) -> None:
	sub = AsyncSubClient(client, 0)
	client.set_language(lang)
	if action == "ban":
		await sub.ban_user(user_id)
		await query.message.edit_text(t("telegram.profile.btn_ban_global", lang))

	elif action == "unban":
		await sub.unban_user(user_id)
		await query.message.edit_text(t("telegram.profile.btn_unban_global", lang))
