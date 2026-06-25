from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import filters
from pyrogram.errors import MessageNotModified

from src.utils.i18n import t
from src import altAminoClient as client
from src.telegram import tgApp as app

from altamino.objects.resp.from_code import FromCode
from altamino import args
from altamino import AsyncSubClient
from src.telegram.helpers.wrappers.adm import admin_only
from src.utils.db import get_language
from src.utils.link_validator import is_altamino_link

_pending: dict[int, dict] = {}


def _chat_keyboard(lang: str) -> InlineKeyboardMarkup:
	return InlineKeyboardMarkup([
		[InlineKeyboardButton(t("telegram.chat.transfer_host_btn", lang), callback_data="transfer_chat_host")],
		[
			InlineKeyboardButton(t("telegram.chat.add_cohost_btn",   lang), callback_data="add_chat_cohost"),
			InlineKeyboardButton(t("telegram.chat.remove_cohost_btn", lang), callback_data="remove_chat_cohost"),
		],
		[InlineKeyboardButton(t("telegram.chat.disable_chat_btn",   lang), callback_data="disable_chat")],
		[InlineKeyboardButton(t("telegram.chat.delete_chat_btn",   lang), callback_data="delete_chat")],
	])


async def handle_chat(reply: Message, link_info: FromCode, lang) -> None:
	user_id = reply.from_user.id if reply.from_user else reply.chat.id
	
	_pending[user_id] = {
		  "chat_info": {"chat_id": link_info.objectId, "com_id": link_info.comId or "0"},
		  "action": None
	}
	await reply.edit_text(t("telegram.chat.panel", lang), reply_markup=_chat_keyboard(lang))


@app.on_callback_query(filters.regex(r"^(transfer_chat_host|add_chat_cohost|remove_chat_cohost)$"))
@admin_only
async def add_chat_cohost_callback(_, query: CallbackQuery):
	lang = get_language(query.from_user.id)
	action = query.data
	
	if query.from_user.id not in _pending:
		await query.answer(t("error_session_expired", lang), show_alert=True)
		return

	_pending[query.from_user.id]["action"] = action
	
	try:
		await query.edit_message_text(
			t("telegram.chat.add_user_text", lang),
			reply_markup=InlineKeyboardMarkup([
				[InlineKeyboardButton(t("telegram.chat.btn_cancel", lang), callback_data="chat_cancel")],
			]),
		)
	except MessageNotModified:
		pass
	await query.answer()


@app.on_message(
	filters.text & filters.private, group=2,
)
async def pending_user_chat_link_handler(_, message: Message):
	user_id = message.from_user.id
	user_session = _pending.get(user_id)
	
	if user_session is None or user_session.get("action") is None:
		return
		
	lang = get_language(user_id)
	reply = await message.reply(t("telegram.links.processing", lang))
	url = message.text
	if url is None or not is_altamino_link(url):
		await reply.edit_text(t("telegram.links.invalid", lang))
		return
	
	try:
		client.set_language(lang)
		link_info = await client.get_from_link(url)
	except Exception as e:
		await reply.edit_text(str(e))
		return

	if link_info.objectType != args.ObjectType.Profile:
		await reply.edit_text(t("telegram.chat.incorrect_link", lang))
		return

	inf = user_session["chat_info"]
	current_action = user_session["action"]
	
	sub = AsyncSubClient(client, inf["com_id"])
	sub.set_language(lang)
	
	try:
		if current_action == "add_chat_cohost":
			await sub.add_co_hosts(inf["chat_id"], [link_info.objectId])
		elif current_action == "remove_chat_cohost":
			await sub.delete_co_host(inf["chat_id"], link_info.objectId)
		elif current_action == "transfer_chat_host":
			await sub.transfer_host(inf["chat_id"], link_info.objectId)
			
		await reply.edit_text(t("telegram.chat.action_success", lang))
	except Exception as e:
		await reply.edit_text(
			t("error", lang).format(error=str(e))
		)
	finally:
		_pending.pop(user_id, None)


@app.on_callback_query(filters.regex(r"^chat_cancel$"))
@admin_only
async def chat_delete_cancel_callback(_, query: CallbackQuery):
	lang = get_language(query.from_user.id)
	user_id = query.from_user.id

	_pending.pop(user_id, None)
	
	try:
		await query.edit_message_text(t("telegram.chat.action_cancelled", lang))
	except MessageNotModified:
		pass
	await query.answer()


# ---------------- Delete Section ----------------

@app.on_callback_query(filters.regex(r"^delete_chat$"))
@admin_only
async def chat_delete_callback(_, query: CallbackQuery):
	lang = get_language(query.from_user.id)
	try:
		await query.edit_message_text(
			t("telegram.chat.delete_confirm_ask", lang),
			reply_markup=InlineKeyboardMarkup([
				[InlineKeyboardButton(t("telegram.chat.btn_cancel",   lang), callback_data="chat_cancel")],
				[InlineKeyboardButton(t("telegram.chat.btn_confirm",   lang), callback_data="delete_chat_confirm")],
			]),
		)
	except MessageNotModified:
		pass
	await query.answer()


@app.on_callback_query(filters.regex(r"^disable_chat$"))
@admin_only
async def chat_delete_callback(_, query: CallbackQuery):
	lang = get_language(query.from_user.id)
	try:
		await query.edit_message_text(
			t("telegram.chat.disable_confirm_ask", lang),
			reply_markup=InlineKeyboardMarkup([
				[InlineKeyboardButton(t("telegram.chat.btn_cancel",   lang), callback_data="chat_cancel")],
				[InlineKeyboardButton(t("telegram.chat.btn_confirm",   lang), callback_data="disable_chat_confirm")],
			]),
		)
	except MessageNotModified:
		pass
	await query.answer()



@app.on_callback_query(filters.regex(r"^disable_chat_confirm$"))
@admin_only
async def chat_disable_confirm_callback(_, query: CallbackQuery):
	lang = get_language(query.from_user.id)
	user_id = query.from_user.id
	
	if user_id not in _pending:
		await query.answer(t("error_session_expired", lang), show_alert=True)
		return
	
	await query.answer(t("unsupported", lang))
	#_pending.pop(user_id, None)
	return

	inf = _pending[user_id]["chat_info"]
	sub = AsyncSubClient(client, inf["com_id"])
	sub.set_language(lang)
	
	try:
		#await sub.(inf["chat_id"])
		await query.message.edit_text(t("telegram.chat.disabled", lang))
	except Exception as e:
		await query.message.edit_text(
			t("error", lang).format(error=str(e)),
		)
	finally:
		_pending.pop(user_id, None)
		await query.answer()





@app.on_callback_query(filters.regex(r"^delete_chat_confirm$"))
@admin_only
async def chat_delete_confirm_callback(_, query: CallbackQuery):
	lang = get_language(query.from_user.id)
	user_id = query.from_user.id
	
	if user_id not in _pending:
		await query.answer(t("error_session_expired", lang), show_alert=True)
		return

	inf = _pending[user_id]["chat_info"]
	sub = AsyncSubClient(client, inf["com_id"])
	sub.set_language(lang)
	
	try:
		await sub.delete_chat(inf["chat_id"])
		await query.message.edit_text(t("telegram.chat.deleted", lang))
	except Exception as e:
		await query.message.edit_text(
			t("error", lang).format(error=str(e)),
		)
	finally:
		_pending.pop(user_id, None)
		await query.answer()