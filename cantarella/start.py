import os
import asyncio
import random
import time
import shutil
import pyrogram
import requests
from pyrogram import Client, filters, enums
from pyrogram.errors import (
    FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant,
    InviteHashExpired, UsernameNotOccupied, AuthKeyUnregistered, UserDeactivated, UserDeactivatedBan
)
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery, InputMediaPhoto
from config import API_ID, API_HASH, ERROR_MESSAGE
from database.db import db
import math
from logger import LOGGER
from cantarella.force_subscribe import is_subscribed, send_force_subscribe

logger = LOGGER(__name__)

SUBSCRIPTION = os.environ.get('SUBSCRIPTION', 'https://graph.org/file/242b7f1b52743938d81f1.jpg')
FREE_LIMIT_SIZE = 2 * 1024 * 1024 * 1024
FREE_LIMIT_DAILY = 10
UPI_ID = os.environ.get("UPI_ID", "your_upi@oksbi")
QR_CODE = os.environ.get("QR_CODE", "https://graph.org/file/242b7f1b52743938d81f1.jpg")

REACTIONS = [
    "👍", "❤️", "🔥", "🥰", "👏", "😁", "🤔", "🤯", "😱", "🤬",
    "😢", "🎉", "🤩", "🤮", "💩", "🙏", "👌", "🕊", "🤡", "🥱",
    "🥴", "😍", "🐳", "❤️‍🔥", "🌚", "🌭", "💯", "🤣", "⚡", "🍌",
    "🏆", "💔", "🤨", "😐", "🍓", "🍾", "💋", "🖕", "😈", "😴",
    "😭", "🤓", "👻", "👨‍💻", "👀", "🎃", "🙈", "😇", "😨", "🤝",
    "✍", "🤗", "🫡", "🎅", "🎄", "☃", "💅", "🤪", "🗿", "🆒",
    "💘", "🙉", "🦄", "😘", "💊", "🙊", "😎", "👾", "🤷‍♂️", "🤷‍♀️",
    "😡"
]

dev_text = "👨‍💻 Mind Behind This Bot:\n• @Mr_Ghunawat01"
channels_text = "📢 Official Channel:\n• @GHUNAWAT_X\n\nStay updated for new features!"


class script(object):

    START_TXT = """<b>👋 Hello {},</b>
<b>🤖 I am <a href=https://t.me/{}>{}</a></b>
<i>Your Professional Restricted Content Saver Bot.</i>
<blockquote><b>🚀 System Status: 🟢 Online</b>
<b>⚡ Performance: 10x High-Speed Processing</b>
<b>🔐 Security: End-to-End Encrypted</b>
<b>📊 Uptime: 99.9% Guaranteed</b></blockquote>
<b>👇 Select an Option Below to Get Started:</b>
"""
    HELP_TXT = """<b>📚 Comprehensive Help & User Guide</b>
<blockquote><b>1️⃣ Public Channels (No Login Required)</b></blockquote>
• Forward or send the post link directly.
• Compatible with any public channel or group.
• <i>Example Link:</i> <code>https://t.me/channel/123</code>
<blockquote><b>2️⃣ Private/Restricted Channels (Login Required)</b></blockquote>
• Use <code>/login</code> to securely connect your Telegram account.
• Send the private link (e.g., <code>t.me/c/123...</code>).
• Bot accesses content using your authenticated session.
<blockquote><b>3️⃣ Batch Downloading Mode</b></blockquote>
• Send a link with range like: <code>https://t.me/channel/100-200</code>
• Use <code>/cancel</code> to stop any running batch.
<blockquote><b>🛑 Free User Limitations:</b></blockquote>
• <b>Daily Quota:</b> 10 Files / 24 Hours
• <b>File Size Cap:</b> 2GB Maximum
<blockquote><b>💎 Premium Membership Benefits:</b></blockquote>
• Unlimited Downloads & No Restrictions.
• Priority Support & Advanced Features.
"""
    ABOUT_TXT = """<b>ℹ️ About This Bot</b>
<blockquote><b>╭────[ 🧩 Technical Stack ]────⍟</b>
<b>├⍟ 🤖 Bot Name : 𝔾ℍ𝕌ℕ𝔸𝕎𝔸𝕋_𝕏</b>
<b>├⍟ 👨‍💻 Owner : <a href=https://t.me/Ghunawat_x_bot>Ghunawat_x_bot</a></b>
<b>├⍟ 📚 Library : <a href='https://docs.pyrogram.org/'>Pyrogram Async</a></b>
<b>├⍟ 🐍 Language : <a href='https://www.python.org/'>Python 3.11+</a></b>
<b>├⍟ 🗄 Database : <a href='https://www.mongodb.com/'>MongoDB Atlas Cluster</a></b>
<b>├⍟ 📢 Channel : <a href='https://t.me/GHUNAWAT_X'>𝔾ℍ𝕌ℕ𝔸𝕎𝔸𝕋_𝕏</a></b>
<b>╰───────────────⍟</b></blockquote>
"""
    PREMIUM_TEXT = """<b>💎 Premium Membership Plans — 𝔾ℍ𝕌ℕ𝔸𝕎𝔸𝕋_𝕏</b>
<b>Unlock Unlimited Access & Advanced Features!</b>
<blockquote><b>✨ Key Benefits:</b>
<b>♾️ Unlimited Daily Downloads</b>
<b>📂 Support for 4GB+ File Sizes</b>
<b>⚡ Instant Processing (Zero Delay)</b>
<b>🖼 Customizable Thumbnails</b>
<b>📝 Personalized Captions</b>
<b>🛂 24/7 Priority Support</b></blockquote>
<blockquote><b>💳 Pricing Options:</b></blockquote>
• <b>1 Month Plan:</b> ₹50 / $1 (Billed Monthly)
• <b>3 Month Plan:</b> ₹120 / $2.5 (Save 20%)
• <b>Lifetime Access:</b> ₹200 / $4 (One-Time Payment)
<blockquote><b>👇 Secure Payment:</b></blockquote>
<b>💸 UPI ID:</b> <code>{}</code>
<b>📸 QR Code:</b> <a href='{}'>Scan to Pay</a>
<i>After Payment: Send Screenshot to Admin for Instant Activation.</i>
"""
    PROGRESS_BAR = """\
<b>⚡ Processing Task...</b>
<blockquote>
<b>Progress: {bar} {percentage:.1f}%</b>
<b>🚀 Speed:</b> <code>{speed}/s</code>
<b>💾 Size:</b> <code>{current} of {total}</code>
<b>⏱ Elapsed:</b> <code>{elapsed}</code>
<b>⏳ ETA:</b> <code>{eta}</code>
</blockquote>
"""
    CAPTION = """<b>Powered By : <a href="https://t.me/Ghunawat_x_bot">𝔾ℍ𝕌ℕ𝔸𝕎𝔸𝕋_𝕏</a></b>"""
    LIMIT_REACHED = """<b>🚫 Daily Limit Exceeded</b>
<b>Your 10 free saves for today have been used.</b>
<i>Quota resets automatically after 24 hours from first download.</i>
<blockquote><b>🔓 Upgrade to Premium for Unlimited Access!</b></blockquote>
Remove all restrictions and enjoy seamless downloading.
"""
    SIZE_LIMIT = """<b>⚠️ File Size Exceeded</b>
<b>Free tier limited to 2GB per file.</b>
<blockquote><b>🔓 Upgrade to Premium</b></blockquote>
Download files up to 4GB and beyond with no limits!
"""


def humanbytes(size):
    if not size:
        return "0B"
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'


def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "")
    return tmp[:-2] if tmp else "0s"


class batch_temp(object):
    IS_BATCH = {}


def get_message_type(msg):
    if getattr(msg, 'animation', None): return "Animation"   # GIF pehle check karo
    if getattr(msg, 'document', None): return "Document"
    if getattr(msg, 'video', None): return "Video"
    if getattr(msg, 'photo', None): return "Photo"
    if getattr(msg, 'audio', None): return "Audio"
    if getattr(msg, 'text', None): return "Text"
    return None


def passes_filter(msg_type, mime_type, filter_mode):
    if filter_mode == "all":
        return True
    if filter_mode == "pdf_video":
        is_pdf = (msg_type == "Document" and mime_type == "application/pdf")
        is_video = msg_type == "Video"
        return is_pdf or is_video
    if filter_mode == "text_gif":
        return msg_type not in ("Text", "Animation")  # Text aur GIF skip, baaki sab download
    return True


async def downstatus(client, statusfile, message, chat):
    while not os.path.exists(statusfile):
        await asyncio.sleep(3)
    while os.path.exists(statusfile):
        try:
            with open(statusfile, "r", encoding='utf-8') as downread:
                txt = downread.read()
            await client.edit_message_text(chat, message.id, f"{txt}")
            await asyncio.sleep(5)
        except:
            await asyncio.sleep(5)


async def upstatus(client, statusfile, message, chat):
    while not os.path.exists(statusfile):
        await asyncio.sleep(3)
    while os.path.exists(statusfile):
        try:
            with open(statusfile, "r", encoding='utf-8') as upread:
                txt = upread.read()
            await client.edit_message_text(chat, message.id, f"{txt}")
            await asyncio.sleep(5)
        except:
            await asyncio.sleep(5)


def progress(current, total, message, type):
    if batch_temp.IS_BATCH.get(message.from_user.id):
        raise Exception("Cancelled")
    if not hasattr(progress, "cache"):
        progress.cache = {}

    now = time.time()
    task_id = f"{message.id}{type}"
    last_time = progress.cache.get(task_id, 0)

    if not hasattr(progress, "start_time"):
        progress.start_time = {}
    if task_id not in progress.start_time:
        progress.start_time[task_id] = now

    if (now - last_time) > 5 or current == total:
        try:
            percentage = current * 100 / total
            speed = current / (now - progress.start_time[task_id]) if (now - progress.start_time[task_id]) > 0 else 0
            eta = (total - current) / speed if speed > 0 else 0
            elapsed = now - progress.start_time[task_id]

            filled_length = int(percentage / 5)
            bar = '█' * filled_length + ' ' * (20 - filled_length)

            status = script.PROGRESS_BAR.format(
                bar=bar,
                percentage=percentage,
                current=humanbytes(current),
                total=humanbytes(total),
                speed=humanbytes(speed),
                elapsed=TimeFormatter(elapsed * 1000),
                eta=TimeFormatter(eta * 1000)
            )

            with open(f'{message.id}{type}status.txt', "w", encoding='utf-8') as fileup:
                fileup.write(status)

            progress.cache[task_id] = now

            if current == total:
                progress.start_time.pop(task_id, None)
                progress.cache.pop(task_id, None)
        except:
            pass


@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)

    if not await is_subscribed(client, message.from_user.id):
        return await send_force_subscribe(message)

    try:
        await message.react(emoji=random.choice(REACTIONS), big=True)
    except:
        pass

    photo_url = "https://i.postimg.cc/kX9tjGXP/16.png"

    buttons = [
        [
            InlineKeyboardButton("💎 Buy Premium", callback_data="buy_premium"),
            InlineKeyboardButton("🆘 Help & Guide", callback_data="help_btn")
        ],
        [
            InlineKeyboardButton("⚙️ Settings Panel", callback_data="settings_btn"),
            InlineKeyboardButton("ℹ️ About Bot", callback_data="about_btn")
        ],
        [
            InlineKeyboardButton('📢 Channel', url="https://t.me/GHUNAWAT_X"),
            InlineKeyboardButton('👨‍💻 Owner', url="https://t.me/Ghunawat_x_bot")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    bot = await client.get_me()
    await client.send_photo(
        chat_id=message.chat.id,
        photo=photo_url,
        caption=script.START_TXT.format(message.from_user.mention, bot.username, bot.first_name),
        reply_markup=reply_markup,
        reply_to_message_id=message.id,
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    if not await is_subscribed(client, message.from_user.id):
        return await send_force_subscribe(message)

    buttons = [[InlineKeyboardButton("❌ Close Menu", callback_data="close_btn")]]
    await client.send_message(
        chat_id=message.chat.id,
        text=script.HELP_TXT,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_message(filters.command(["plan", "myplan", "premium"]))
async def send_plan(client: Client, message: Message):
    if not await is_subscribed(client, message.from_user.id):
        return await send_force_subscribe(message)

    buttons = [
        [InlineKeyboardButton("📸 Send Payment Proof", url="https://t.me/Ghunawat_x_bot")],
        [InlineKeyboardButton("❌ Close Menu", callback_data="close_btn")]
    ]
    await client.send_photo(
        chat_id=message.chat.id,
        photo=SUBSCRIPTION,
        caption=script.PREMIUM_TEXT.format(UPI_ID, QR_CODE),
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_message(filters.command(["batch"]))
async def send_batch_help(client: Client, message: Message):
    if not await is_subscribed(client, message.from_user.id):
        return await send_force_subscribe(message)

    await message.reply_text(
        "<b>📦 Batch Download Mode — 𝔾ℍ𝕌ℕ𝔸𝕎𝔸𝕋_𝕏</b>\n\n"
        "<b>Batch download ke liye link mein range daalein:</b>\n\n"
        "<b>Public Channel:</b>\n"
        "<code>https://t.me/channelname/100-200</code>\n\n"
        "<b>Private Channel:</b>\n"
        "<code>https://t.me/c/1234567890/100-200</code>\n\n"
        "<blockquote>Yahan <code>100</code> start message ID aur <code>200</code> end message ID hai.</blockquote>\n\n"
        "⚠️ Private channel ke liye pehle <b>/login</b> karein.\n"
        "❌ Chal rahi batch rok ne ke liye <b>/cancel</b> bhejein.",
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    user_id = message.from_user.id
    if batch_temp.IS_BATCH.get(user_id) == False:
        batch_temp.IS_BATCH[user_id] = True
        await message.reply_text("❌ <b>Batch Process Cancel Ho Raha Hai...</b>\n<i>Current file complete hone ke baad rukega.</i>", parse_mode=enums.ParseMode.HTML)
    else:
        await message.reply_text("⚠️ <b>Koi bhi task chal nahi raha hai.</b>", parse_mode=enums.ParseMode.HTML)


async def settings_panel(client, callback_query):
    user_id = callback_query.from_user.id
    is_premium = await db.check_premium(user_id)
    badge = "💎 Premium Member" if is_premium else "👤 Standard User"

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📜 Command List", callback_data="cmd_list_btn")],
        [InlineKeyboardButton("📊 Usage Stats", callback_data="user_stats_btn")],
        [InlineKeyboardButton("🗑 Dump Chat Settings", callback_data="dump_chat_btn")],
        [InlineKeyboardButton("🖼 Manage Thumbnail", callback_data="thumb_btn")],
        [InlineKeyboardButton("📝 Edit Caption", callback_data="caption_btn")],
        [InlineKeyboardButton("⬅️ Return to Home", callback_data="start_btn")]
    ])

    text = f"<b>⚙️ Settings Dashboard</b>\n\n<b>Account Status:</b> {badge}\n<b>User ID:</b> <code>{user_id}</code>\n\n<i>Customize and manage your bot preferences below for an optimized experience:</i>"

    await callback_query.edit_message_caption(
        caption=text,
        reply_markup=buttons,
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_message(filters.text & filters.private & ~filters.regex("^/"))
async def save(client: Client, message: Message):
    if "https://t.me/" not in message.text:
        return

    if not await is_subscribed(client, message.from_user.id):
        return await send_force_subscribe(message)

    is_limit_reached = await db.check_limit(message.from_user.id)
    if is_limit_reached:
        btn = InlineKeyboardMarkup([[InlineKeyboardButton("💎 Upgrade to Premium", callback_data="buy_premium")]])
        return await message.reply_photo(
            photo=SUBSCRIPTION,
            caption=script.LIMIT_REACHED,
            reply_markup=btn,
            parse_mode=enums.ParseMode.HTML
        )

    if batch_temp.IS_BATCH.get(message.from_user.id) == False:
        return await message.reply_text(
            "<b>⚠️ Ek Task Abhi Chal Raha Hai.</b>\n<i>Complete hone ka wait karo ya /cancel bhejo.</i>",
            parse_mode=enums.ParseMode.HTML
        )

    datas = message.text.split("/")
    temp = datas[-1].replace("?single", "").split("-")
    fromID = int(temp[0].strip())
    try:
        toID = int(temp[1].strip())
    except:
        toID = fromID

    batch_temp.IS_BATCH[message.from_user.id] = False

    is_private_link = "https://t.me/c/" in message.text
    is_batch = "https://t.me/b/" in message.text
    is_public_link = not is_private_link and not is_batch

    acc = None
    if not is_public_link:
        user_data = await db.get_session(message.from_user.id)
        if user_data is None:
            batch_temp.IS_BATCH[message.from_user.id] = True
            return await message.reply(
                "<b>🔒 Login Zaroori Hai</b>\n\n"
                "<i>Private content ke liye pehle /login karein.</i>",
                parse_mode=enums.ParseMode.HTML
            )
        try:
            acc = Client(
                "saverestricted",
                session_string=user_data,
                api_hash=API_HASH,
                api_id=API_ID,
                in_memory=True,
                max_concurrent_transmissions=10
            )
            await acc.connect()
        except Exception as e:
            batch_temp.IS_BATCH[message.from_user.id] = True
            return await message.reply(
                f"<b>❌ Authentication Failed</b>\n\n<i>Session expire ho gayi. /logout karke dobara /login karein.</i>\n<code>{e}</code>",
                parse_mode=enums.ParseMode.HTML
            )

    for msgid in range(fromID, toID + 1):

        if batch_temp.IS_BATCH.get(message.from_user.id):
            break

        if is_public_link:
            username = datas[3]
            try:
                pub_msg = await client.get_messages(username, msgid)
                if not pub_msg or pub_msg.empty:
                    await asyncio.sleep(1)
                    continue

                pub_msg_type = get_message_type(pub_msg)
                filter_mode = await db.get_filter_mode(message.from_user.id)
                pub_mime = getattr(pub_msg.document, 'mime_type', '') if pub_msg_type == "Document" else ''

                if not passes_filter(pub_msg_type, pub_mime, filter_mode):
                    await asyncio.sleep(0.5)
                    continue

                await client.copy_message(
                    chat_id=message.chat.id,
                    from_chat_id=username,
                    message_id=msgid,
                    reply_to_message_id=message.id
                )
                await db.add_traffic(message.from_user.id)
            except Exception as e:
                pass

            if batch_temp.IS_BATCH.get(message.from_user.id):
                break

            await asyncio.sleep(1)
            continue

        if is_private_link:
            chatid = int("-100" + datas[4])
            await handle_restricted_content(client, acc, message, chatid, msgid)
        elif is_batch:
            username = datas[4]
            await handle_restricted_content(client, acc, message, username, msgid)
        else:
            username = datas[3]
            await handle_restricted_content(client, acc, message, username, msgid)

        if batch_temp.IS_BATCH.get(message.from_user.id):
            break

        await asyncio.sleep(2)

    if acc:
        try:
            await acc.disconnect()
        except:
            pass

    batch_temp.IS_BATCH[message.from_user.id] = True


async def handle_restricted_content(client: Client, acc, message: Message, chat_target, msgid):
    try:
        msg: Message = await acc.get_messages(chat_target, msgid)
    except Exception as e:
        logger.error(f"Error fetching message: {e}")
        return
    if msg.empty:
        return

    msg_type = get_message_type(msg)
    if not msg_type:
        return

    filter_mode = await db.get_filter_mode(message.from_user.id)
    mime = getattr(msg.document, 'mime_type', '') if msg_type == "Document" else ''
    if not passes_filter(msg_type, mime, filter_mode):
        return

    file_size = 0
    if msg_type == "Document": file_size = msg.document.file_size
    elif msg_type == "Video": file_size = msg.video.file_size
    elif msg_type == "Audio": file_size = msg.audio.file_size

    if file_size > FREE_LIMIT_SIZE:
        if not await db.check_premium(message.from_user.id):
            btn = InlineKeyboardMarkup([[InlineKeyboardButton("💎 Upgrade to Premium", callback_data="buy_premium")]])
            await client.send_message(
                message.chat.id,
                script.SIZE_LIMIT,
                reply_markup=btn,
                parse_mode=enums.ParseMode.HTML
            )
            return

    dump_chat = await db.get_dump_chat(message.from_user.id)
    target_chat = dump_chat if dump_chat else message.chat.id

    if msg_type == "Text":
        try:
            await client.send_message(target_chat, msg.text, entities=msg.entities, parse_mode=enums.ParseMode.HTML)
            return
        except:
            return

    await db.add_traffic(message.from_user.id)
    smsg = await client.send_message(
        message.chat.id,
        '<b>⬇️ Download Shuru Ho Raha Hai...</b>',
        reply_to_message_id=message.id,
        parse_mode=enums.ParseMode.HTML
    )

    temp_dir = f"downloads/{message.id}"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    try:
        asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg, message.chat.id))

        file = await acc.download_media(
            msg,
            file_name=f"{temp_dir}/",
            progress=progress,
            progress_args=[message, "down"]
        )

        if os.path.exists(f'{message.id}downstatus.txt'):
            os.remove(f'{message.id}downstatus.txt')

    except Exception as e:
        if batch_temp.IS_BATCH.get(message.from_user.id) or "Cancelled" in str(e):
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            return await smsg.edit("❌ <b>Task Cancel Kar Diya Gaya</b>", parse_mode=enums.ParseMode.HTML)
        return await smsg.delete()

    try:
        asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg, message.chat.id))

        ph_path = None
        thumb_id = await db.get_thumbnail(message.from_user.id)

        if thumb_id:
            try:
                ph_path = await client.download_media(thumb_id, file_name=f"{temp_dir}/custom_thumb.jpg")
            except Exception as e:
                logger.error(f"Failed to download custom thumb: {e}")

        if not ph_path:
            try:
                if msg_type == "Video" and msg.video.thumbs:
                    ph_path = await acc.download_media(msg.video.thumbs[0].file_id, file_name=f"{temp_dir}/thumb.jpg")
                elif msg_type == "Document" and msg.document.thumbs:
                    ph_path = await acc.download_media(msg.document.thumbs[0].file_id, file_name=f"{temp_dir}/thumb.jpg")
            except:
                pass

        custom_caption = await db.get_caption(message.from_user.id)
        if custom_caption:
            final_caption = custom_caption.format(filename=file.split("/")[-1], size=humanbytes(file_size))
        else:
            final_caption = script.CAPTION
            if msg.caption:
                final_caption += f"\n\n{msg.caption}"

        if msg_type == "Document":
            await client.send_document(
                target_chat, file, thumb=ph_path, caption=final_caption,
                progress=progress, progress_args=[message, "up"]
            )
        elif msg_type == "Video":
            await client.send_video(
                target_chat, file,
                duration=msg.video.duration, width=msg.video.width, height=msg.video.height,
                thumb=ph_path, caption=final_caption,
                progress=progress, progress_args=[message, "up"]
            )
        elif msg_type == "Audio":
            await client.send_audio(
                target_chat, file, thumb=ph_path, caption=final_caption,
                progress=progress, progress_args=[message, "up"]
            )
        elif msg_type == "Photo":
            await client.send_photo(target_chat, file, caption=final_caption)

    except Exception as e:
        await smsg.edit(f"❌ Upload Failed: {e}")

    if os.path.exists(f'{message.id}upstatus.txt'):
        os.remove(f'{message.id}upstatus.txt')
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    await client.delete_messages(message.chat.id, [smsg.id])


@Client.on_callback_query()
async def button_callbacks(client: Client, callback_query: CallbackQuery):
    data = callback_query.data
    message = callback_query.message
    if not message:
        return

    if data == "dev_info":
        await callback_query.answer(text=dev_text, show_alert=True)
    elif data == "channels_info":
        await callback_query.answer(text=channels_text, show_alert=True)
    elif data == "settings_btn":
        await settings_panel(client, callback_query)
    elif data == "buy_premium":
        buttons = [
            [InlineKeyboardButton("📸 Send Payment Proof", url="https://t.me/Mr_Ghunawat01")],
            [InlineKeyboardButton("⬅️ Back to Home", callback_data="start_btn")]
        ]
        await client.edit_message_media(
            chat_id=message.chat.id,
            message_id=message.id,
            media=InputMediaPhoto(
                media=SUBSCRIPTION,
                caption=script.PREMIUM_TEXT.format(UPI_ID, QR_CODE)
            ),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    elif data == "help_btn":
        buttons = [[InlineKeyboardButton("⬅️ Back to Home", callback_data="start_btn")]]
        await client.edit_message_caption(
            chat_id=message.chat.id,
            message_id=message.id,
            caption=script.HELP_TXT,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )
    elif data == "about_btn":
        buttons = [[InlineKeyboardButton("⬅️ Back to Home", callback_data="start_btn")]]
        await client.edit_message_caption(
            chat_id=message.chat.id,
            message_id=message.id,
            caption=script.ABOUT_TXT,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )
    elif data == "start_btn":
        bot = await client.get_me()
        photo_url = "https://i.postimg.cc/cC7txyhz/15.png"
        buttons = [
            [
                InlineKeyboardButton("💎 Buy Premium", callback_data="buy_premium"),
                InlineKeyboardButton("🆘 Help & Guide", callback_data="help_btn")
            ],
            [
                InlineKeyboardButton("⚙️ Settings Panel", callback_data="settings_btn"),
                InlineKeyboardButton("ℹ️ About Bot", callback_data="about_btn")
            ],
            [
                InlineKeyboardButton('📢 Channel', url="https://t.me/GHUNAWAT_X"),
                InlineKeyboardButton('👨‍💻 Owner', url="https://t.me/Mr_Ghunawat01")
            ]
        ]
        await client.edit_message_media(
            chat_id=message.chat.id,
            message_id=message.id,
            media=InputMediaPhoto(
                media=photo_url,
                caption=script.START_TXT.format(callback_query.from_user.mention, bot.username, bot.first_name)
            ),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    elif data == "close_btn":
        await message.delete()
    elif data in ["cmd_list_btn", "user_stats_btn", "dump_chat_btn", "thumb_btn", "caption_btn"]:
        pass

    await callback_query.answer()
