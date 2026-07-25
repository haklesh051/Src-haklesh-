# cantarella
# Don't Remove Credit
# Telegram Channel @cantarellabots

from pyrogram import Client, filters, enums
from pyrogram.types import Message
from database.db import db

# ======================================================
# /set_del_word - Ek ya bahut se words delete list mein add karo
# Usage: /set_del_word word1 word2 word3 ...
# ======================================================
@Client.on_message(filters.command("set_del_word") & filters.private)
async def set_del_word(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "<b>📝 Delete Words — Usage</b>\n\n"
            "<b>Ek word:</b>\n"
            "<code>/set_del_word badword</code>\n\n"
            "<b>Bahut se words ek saath:</b>\n"
            "<code>/set_del_word word1 word2 word3</code>\n\n"
            "<i>Ye words captions aur filenames se automatically hata diye jayenge.</i>",
            parse_mode=enums.ParseMode.HTML
        )

    words = message.command[1:]
    await db.set_delete_words(message.from_user.id, words)

    word_list = "\n".join([f"• <code>{w}</code>" for w in words])
    await message.reply_text(
        f"<b>✅ {len(words)} Word(s) Delete List Mein Add Ho Gaye</b>\n\n"
        f"{word_list}",
        parse_mode=enums.ParseMode.HTML
    )


# ======================================================
# /rem_del_word - Delete list se words hatao
# Usage: /rem_del_word word1 word2 ...
# ======================================================
@Client.on_message(filters.command("rem_del_word") & filters.private)
async def rem_del_word(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "<b>📝 Remove Delete Words — Usage</b>\n\n"
            "<code>/rem_del_word word1 word2 word3</code>",
            parse_mode=enums.ParseMode.HTML
        )

    words = message.command[1:]
    await db.remove_delete_words(message.from_user.id, words)

    word_list = "\n".join([f"• <code>{w}</code>" for w in words])
    await message.reply_text(
        f"<b>✅ {len(words)} Word(s) Delete List Se Hata Diye</b>\n\n"
        f"{word_list}",
        parse_mode=enums.ParseMode.HTML
    )


# ======================================================
# /see_del_word - Delete list dekho
# ======================================================
@Client.on_message(filters.command("see_del_word") & filters.private)
async def see_del_word(client: Client, message: Message):
    words = await db.get_delete_words(message.from_user.id)
    if not words:
        return await message.reply_text(
            "<b>❌ Koi Delete Word Set Nahi Hai</b>\n\n"
            "<i>/set_del_word se add karo.</i>",
            parse_mode=enums.ParseMode.HTML
        )
    word_list = "\n".join([f"• <code>{w}</code>" for w in words])
    await message.reply_text(
        f"<b>📋 Aapki Delete Words List ({len(words)} words)</b>\n\n"
        f"{word_list}",
        parse_mode=enums.ParseMode.HTML
    )


# ======================================================
# /set_repl_word - Ek ya bahut se replace pairs ek saath
#
# Format (ek pair):
#   /set_repl_word purana=naya
#
# Format (bahut se pairs — | se alag karo):
#   /set_repl_word word1=new1 | word2=new2 | word3=new3
#
# Example:
#   /set_repl_word @OldCh=@NewCh | BadName=GoodName | Hello=Hola
# ======================================================
@Client.on_message(filters.command("set_repl_word") & filters.private)
async def set_repl_word(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "<b>🔄 Replace Words — Usage</b>\n\n"
            "<b>Ek pair:</b>\n"
            "<code>/set_repl_word purana=naya</code>\n\n"
            "<b>Bahut se pairs ek saath ( | se alag karo):</b>\n"
            "<code>/set_repl_word word1=new1 | word2=new2 | word3=new3</code>\n\n"
            "<b>Example:</b>\n"
            "<code>/set_repl_word @OldChannel=@NewChannel | BadWord=GoodWord | Name1=Name2</code>\n\n"
            "<i>Bot automatically captions mein ye replacements lagayega.</i>",
            parse_mode=enums.ParseMode.HTML
        )

    full_text = message.text.split(None, 1)[1]
    raw_pairs = [p.strip() for p in full_text.split("|") if p.strip()]

    added = {}
    errors = []

    for pair in raw_pairs:
        if "=" not in pair:
            errors.append(f"<code>{pair}</code> → format galat hai (= nahi mila)")
            continue
        parts = pair.split("=", 1)
        target = parts[0].strip()
        replacement = parts[1].strip()
        if not target:
            errors.append(f"<code>{pair}</code> → purana word khaali hai")
            continue
        added[target] = replacement

    if not added:
        error_text = "\n".join(errors) if errors else "Koi valid pair nahi mila."
        return await message.reply_text(
            f"<b>❌ Koi Pair Add Nahi Hua</b>\n\n{error_text}",
            parse_mode=enums.ParseMode.HTML
        )

    await db.set_replace_words(message.from_user.id, added)

    pair_list = "\n".join([f"• <code>{k}</code>  →  <code>{v}</code>" for k, v in added.items()])
    result_text = f"<b>✅ {len(added)} Replace Pair(s) Save Ho Gaye</b>\n\n{pair_list}"

    if errors:
        err_text = "\n".join(errors)
        result_text += f"\n\n<b>⚠️ Ye Skip Ho Gaye (format galat):</b>\n{err_text}"

    await message.reply_text(result_text, parse_mode=enums.ParseMode.HTML)


# ======================================================
# /rem_repl_word - Replace list se words hatao
# Usage: /rem_repl_word word1 | word2 | word3
# ======================================================
@Client.on_message(filters.command("rem_repl_word") & filters.private)
async def rem_repl_word(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "<b>📝 Remove Replace Words — Usage</b>\n\n"
            "<b>Ek:</b> <code>/rem_repl_word word1</code>\n"
            "<b>Bahut se:</b> <code>/rem_repl_word word1 | word2 | word3</code>",
            parse_mode=enums.ParseMode.HTML
        )

    full_text = message.text.split(None, 1)[1]
    targets = [t.strip() for t in full_text.split("|") if t.strip()]

    await db.remove_replace_words(message.from_user.id, targets)

    word_list = "\n".join([f"• <code>{t}</code>" for t in targets])
    await message.reply_text(
        f"<b>✅ {len(targets)} Replace Pair(s) Hata Diye</b>\n\n{word_list}",
        parse_mode=enums.ParseMode.HTML
    )


# ======================================================
# /see_repl_word - Apni saari replace list dekho
# ======================================================
@Client.on_message(filters.command("see_repl_word") & filters.private)
async def see_repl_word(client: Client, message: Message):
    repl = await db.get_replace_words(message.from_user.id)
    if not repl:
        return await message.reply_text(
            "<b>❌ Koi Replace Word Set Nahi Hai</b>\n\n"
            "<i>/set_repl_word se add karo.</i>",
            parse_mode=enums.ParseMode.HTML
        )
    pair_list = "\n".join([f"• <code>{k}</code>  →  <code>{v}</code>" for k, v in repl.items()])
    await message.reply_text(
        f"<b>🔄 Aapki Replace Words List ({len(repl)} pairs)</b>\n\n{pair_list}",
        parse_mode=enums.ParseMode.HTML
    )


# ======================================================
# /clear_repl_word - Saari replace list ek saath clear karo
# ======================================================
@Client.on_message(filters.command("clear_repl_word") & filters.private)
async def clear_repl_word(client: Client, message: Message):
    await db.col.update_one({'id': int(message.from_user.id)}, {'$set': {'replace_words': {}}})
    await message.reply_text(
        "<b>✅ Saari Replace List Clear Ho Gayi</b>",
        parse_mode=enums.ParseMode.HTML
    )

# cantarella
# Don't Remove Credit
# Telegram Channel @cantarellabots
