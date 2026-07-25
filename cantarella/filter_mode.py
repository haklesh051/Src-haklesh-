from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.db import db

FILTER_OPTIONS = {
    "all":       ("📂", "Sab Kuch (No Filter)"),
    "pdf_video": ("🎬", "Sirf PDF + Video"),
    "text_gif":  ("🚫", "Text + GIF Skip Karo"),
}


def build_filter_keyboard(current: str) -> InlineKeyboardMarkup:
    rows = []
    for mode, (icon, label) in FILTER_OPTIONS.items():
        tick = "✅ " if current == mode else ""
        rows.append([InlineKeyboardButton(f"{tick}{icon} {label}", callback_data=f"filter_{mode}")])
    rows.append([InlineKeyboardButton("❌ Close", callback_data="close_btn")])
    return InlineKeyboardMarkup(rows)


def filter_description(mode: str) -> str:
    descriptions = {
        "all":       "Koi filter nahi — sab kuch (text, photo, video, pdf, gif, audio) forward hoga.",
        "pdf_video": "Sirf <b>PDF files</b> aur <b>Videos</b> forward honge. Baki sab skip.",
        "text_gif":  "<b>Text</b> aur <b>GIF</b> skip honge. Baaki sab (video, pdf, photo, audio) download hoga.",
    }
    return descriptions.get(mode, "")


@Client.on_message(filters.command("setfilter") & filters.private)
async def setfilter(client: Client, message: Message):
    user_id = message.from_user.id
    current = await db.get_filter_mode(user_id)
    icon, label = FILTER_OPTIONS.get(current, ("📂", "Sab Kuch"))

    await message.reply_text(
        f"<b>🔽 Filter Settings</b>\n\n"
        f"<b>Current Mode:</b> {icon} <b>{label}</b>\n\n"
        f"<i>{filter_description(current)}</i>\n\n"
        f"Neeche se apna filter chunein:",
        reply_markup=build_filter_keyboard(current),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_message(filters.command("myfilter") & filters.private)
async def myfilter(client: Client, message: Message):
    user_id = message.from_user.id
    current = await db.get_filter_mode(user_id)
    icon, label = FILTER_OPTIONS.get(current, ("📂", "Sab Kuch"))

    await message.reply_text(
        f"<b>🔽 Aapka Current Filter</b>\n\n"
        f"Mode: {icon} <b>{label}</b>\n\n"
        f"<i>{filter_description(current)}</i>\n\n"
        f"Change karne ke liye: /setfilter",
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex(r"^filter_(all|pdf_video|text_gif)$"))
async def filter_callback(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    mode = callback_query.data.replace("filter_", "")

    await db.set_filter_mode(user_id, mode)

    icon, label = FILTER_OPTIONS.get(mode, ("📂", "Sab Kuch"))

    await callback_query.edit_message_text(
        f"<b>🔽 Filter Settings</b>\n\n"
        f"<b>Current Mode:</b> {icon} <b>{label}</b>\n\n"
        f"<i>{filter_description(mode)}</i>\n\n"
        f"Neeche se apna filter chunein:",
        reply_markup=build_filter_keyboard(mode),
        parse_mode=enums.ParseMode.HTML
    )
    await callback_query.answer(f"✅ Filter set: {label}")
