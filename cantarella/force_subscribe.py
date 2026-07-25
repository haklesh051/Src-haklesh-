from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant

FORCE_CHANNEL = "GHUNAWAT_X"
FORCE_CHANNEL_LINK = "https://t.me/GHUNAWAT_X"
FORCE_CHANNEL_NAME = "𝔾ℍ𝕌ℕ𝔸𝕎𝔸𝕋_𝕏"

async def is_subscribed(client: Client, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(FORCE_CHANNEL, user_id)
        return member.status.value not in ("left", "banned", "kicked")
    except UserNotParticipant:
        return False
    except Exception:
        return True

async def send_force_subscribe(message: Message):
    btn = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"📢 Join {FORCE_CHANNEL_NAME}", url=FORCE_CHANNEL_LINK)],
        [InlineKeyboardButton("✅ Maine Join Kar Liya", callback_data="check_sub")]
    ])
    await message.reply_text(
        f"<b>⚠️ Channel Join Zaroori Hai!</b>\n\n"
        f"Bot use karne ke liye pehle humara channel join karo:\n\n"
        f"👉 <a href='{FORCE_CHANNEL_LINK}'>{FORCE_CHANNEL_NAME}</a>\n\n"
        f"<i>Join karne ke baad <b>✅ Maine Join Kar Liya</b> button dabao.</i>",
        parse_mode=enums.ParseMode.HTML,
        reply_markup=btn,
        disable_web_page_preview=True
    )

@Client.on_callback_query(filters.regex("^check_sub$"))
async def check_subscription_callback(client: Client, callback_query):
    user_id = callback_query.from_user.id
    if await is_subscribed(client, user_id):
        await callback_query.message.delete()
        await callback_query.answer("✅ Verified! Ab bot use kar sakte ho.", show_alert=True)
    else:
        await callback_query.answer(
            f"❌ Aapne abhi join nahi kiya!\n👉 {FORCE_CHANNEL_LINK}",
            show_alert=True
        )
