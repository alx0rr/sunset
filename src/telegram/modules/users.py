from __future__ import annotations

from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import filters

from altamino.objects.resp.from_code import FromCode
from altamino.objects.args.administrators_rank import AltAminoAdminRank
from altamino import args
from altamino import AsyncSubClient
from src import altAminoClient as client
from src.telegram import tgApp as app
from src.telegram.helpers.wrappers.adm import admin_only
from src.utils.i18n import t
from src.utils.db import get_language

_pending: dict[int, dict] = {}


def _skip_keyboard(lang: str) -> InlineKeyboardMarkup:
	return InlineKeyboardMarkup([
		[
			InlineKeyboardButton(t("telegram.profile.btn_skip",   lang), callback_data="skip_reason"),
			InlineKeyboardButton(t("telegram.profile.btn_cancel", lang), callback_data="cancel_action"),
		],
	])


def _cancel_keyboard(lang: str) -> InlineKeyboardMarkup:
	return InlineKeyboardMarkup([
		[InlineKeyboardButton(t("telegram.profile.btn_cancel", lang), callback_data="cancel_action")],
	])


def _community_keyboard(lang: str, user_id: str, com_id: str) -> InlineKeyboardMarkup:
	p = f"profile:{user_id}:{com_id}"
	return InlineKeyboardMarkup([
		[
			InlineKeyboardButton(t("telegram.profile.btn_ban",      lang), callback_data=f"{p}:ban"),
			InlineKeyboardButton(t("telegram.profile.btn_unban",    lang), callback_data=f"{p}:unban"),
		],
		[
			InlineKeyboardButton(t("telegram.profile.btn_hide",     lang), callback_data=f"{p}:hide"),
			InlineKeyboardButton(t("telegram.profile.btn_unhide",   lang), callback_data=f"{p}:unhide"),
		],
		[
			InlineKeyboardButton(t("telegram.profile.btn_warn",     lang), callback_data=f"{p}:warn"),
			InlineKeyboardButton(t("telegram.profile.btn_strike",   lang), callback_data=f"{p}:strike"),
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


def _strike_time_keyboard(lang: str, user_id: str, com_id: str) -> InlineKeyboardMarkup:
	p = f"strike_time:{user_id}:{com_id}"
	return InlineKeyboardMarkup([
		[
			InlineKeyboardButton("1h",  callback_data=f"{p}:{args.StrikeTime.ONE_HOUR}"),
			InlineKeyboardButton("3h",  callback_data=f"{p}:{args.StrikeTime.THREE_HOURS}"),
			InlineKeyboardButton("6h",  callback_data=f"{p}:{args.StrikeTime.SIX_HOURS}"),
			InlineKeyboardButton("12h", callback_data=f"{p}:{args.StrikeTime.TWELVE_HOURS}"),
			InlineKeyboardButton("24h", callback_data=f"{p}:{args.StrikeTime.TWENTY_FOUR_HOURS}"),
		],
		[InlineKeyboardButton(t("telegram.profile.btn_cancel", lang), callback_data="cancel_action")],
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

	elif action == "hide":
		_pending[query.from_user.id] = {
			"action": "hide",
			"user_id": user_id,
			"com_id": com_id,
			"step": "reason",
			"data": {},
		}
		await query.message.edit_text(
			t("telegram.profile.ask_reason_optional", lang),
			reply_markup=_skip_keyboard(lang),
		)

	elif action == "unhide":
		_pending[query.from_user.id] = {
			"action": "unhide",
			"user_id": user_id,
			"com_id": com_id,
			"step": "reason",
			"data": {},
		}
		await query.message.edit_text(
			t("telegram.profile.ask_reason_optional", lang),
			reply_markup=_skip_keyboard(lang),
		)

	elif action == "warn":
		_pending[query.from_user.id] = {
			"action": "warn",
			"user_id": user_id,
			"com_id": com_id,
			"step": "reason",
			"data": {},
		}
		await query.message.edit_text(
			t("telegram.profile.ask_reason", lang),
			reply_markup=_cancel_keyboard(lang),
		)

	elif action == "strike":
		_pending[query.from_user.id] = {
			"action": "strike",
			"user_id": user_id,
			"com_id": com_id,
			"step": "time",
			"data": {},
		}
		await query.message.edit_text(
			t("telegram.profile.ask_strike_time", lang),
			reply_markup=_strike_time_keyboard(lang, user_id, com_id),
		)


@app.on_callback_query(filters.regex(r"^strike_time:([^:]+):([^:]+):(\d+)$"))
@admin_only
async def strike_time_callback(_, query: CallbackQuery):
	_, user_id, com_id, time_val = query.data.split(":")
	lang = get_language(query.from_user.id)
	await query.answer()

	state = _pending.get(query.from_user.id)
	if not state or state["action"] != "strike":
		return

	state["data"]["time"] = int(time_val)
	state["step"] = "reason"
	await query.message.edit_text(
		t("telegram.profile.ask_reason", lang),
		reply_markup=_cancel_keyboard(lang),
	)


@app.on_callback_query(filters.regex(r"^skip_reason$"))
@admin_only
async def skip_reason_callback(_, query: CallbackQuery):
	lang = get_language(query.from_user.id)
	await query.answer()

	state = _pending.get(query.from_user.id)
	if not state or state["action"] not in ("hide", "unhide"):
		return

	sub = AsyncSubClient(client, int(state["com_id"]))
	if state["action"] == "hide":
		try:
			await sub.hide(state["user_id"], reason=None)
			await query.message.edit_text(t("telegram.profile.hided", lang))
		except Exception as e:
			await query.message.reply(
				t("telegram.profile.error", lang).format(error=str(e)),
			)
	else:
		try:
			await sub.unhide(state["user_id"], reason=None)
			await query.message.edit_text(t("telegram.profile.unhided", lang))
		except Exception as e:
			await query.message.reply(
				t("telegram.profile.error", lang).format(error=str(e))
			)

	del _pending[query.from_user.id]


@app.on_callback_query(filters.regex(r"^cancel_action$"))
@admin_only
async def cancel_action_callback(_, query: CallbackQuery):
	lang = get_language(query.from_user.id)
	await query.answer()
	_pending.pop(query.from_user.id, None)
	await query.message.edit_text(t("telegram.profile.action_cancelled", lang))


@app.on_message(
	filters.text & filters.private & ~filters.command(["ping", "help", "start", "mod", "admin_add", "admin_remove"]),
	group=1,
)
async def pending_text_handler(_, message: Message):
	user_id = message.from_user.id
	state = _pending.get(user_id)
	if not state:
		return

	lang = get_language(user_id)
	action = state["action"]
	step = state["step"]
	text = message.text.strip()

	if action == "warn" and step == "reason":
		sub = AsyncSubClient(client, int(state["com_id"]))
		try:
			await sub.warn(state["user_id"], text)
			await message.reply(t("telegram.profile.warned", lang))
		except Exception as e:
			await message.reply(
				t("telegram.profile.error", lang).format(error=str(e)),
			)
		finally:
			del _pending[user_id]

	elif action == "strike":
		if step == "reason":
			state["data"]["reason"] = text
			state["step"] = "title"
			await message.reply(
				t("telegram.profile.ask_title", lang),
				reply_markup=_cancel_keyboard(lang),
			)
		elif step == "title":
			state["data"]["title"] = text
			sub = AsyncSubClient(client, int(state["com_id"]))
			try:
				await sub.strike(
				state["user_id"],
				state["data"]["time"],
				state["data"]["reason"],
				state["data"]["title"],
			)
				await message.reply(t("telegram.profile.striked", lang))
			except Exception as e:
				await message.reply(
					t("telegram.profile.error", lang).format(error=str(e)),
				)
			finally:
				del _pending[user_id]

	elif action in ("hide", "unhide") and step == "reason":
		sub = AsyncSubClient(client, int(state["com_id"]))
		try:
			if action == "hide":
				await sub.hide(state["user_id"], reason=text)
				await message.reply(t("telegram.profile.hided", lang))
			else:
				await sub.unhide(state["user_id"], reason=text)
				await message.reply(t("telegram.profile.unhided", lang))
		except Exception as e:
			await message.reply(
				t("telegram.profile.error", lang).format(error=str(e)),
				)
		finally:
			del _pending[user_id]


async def _handle_global_action(
	action: str, user_id: str, lang: str, query: CallbackQuery
) -> None:
	if action == "ban":
		await query.message.edit_text(t("unsupported", lang))
	elif action == "unban":
		await query.message.edit_text(t("unsupported", lang))