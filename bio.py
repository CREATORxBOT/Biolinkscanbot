"""
Author: Rohit
User: https://t.me/FZ_CREATOR 
Channel: https://t.me/FZ_LINK
"""

from pyrogram import Client, filters, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions

from helper.utils import (
    is_admin,
    get_config, update_config,
    increment_warning, reset_warnings,
    is_whitelisted, add_whitelist, remove_whitelist, get_whitelist
)

from config import (
    API_ID,
    API_HASH,
    BOT_TOKEN,
    URL_PATTERN
)

app = Client(
    "biolink_protector_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

@app.on_message(filters.command("start"))
async def start_handler(client: Client, message):
    chat_id = message.chat.id
    bot = await client.get_me()
    add_url = f"https://t.me/{bot.username}?startgroup=true"
    text = (
        "**✨ Welcome to BioLink Protector Bot! ✨**\n\n"
        "🛡️ I help protect your groups from users with links in their bio.\n\n"
        "**🔹 Key Features:**\n"
        "   • Automatic URL detection in user bios\n"
        "   • Customizable warning limit\n"
        "   • Auto-mute or ban when limit is reached\n"
        "   • Whitelist management for trusted users\n\n"
        "**Use /help to see all available commands.**"
    )
    kb = InlineKeyboardMarkup([
    [InlineKeyboardButton("➕ Add Me to Your Group", url=add_url)],
    [
        InlineKeyboardButton("🛠️ 𝐒𝐔𝐏𝐏𝐎𝐑𝐓", url="https://t.me/BOT_X_SUPPORT"),
        InlineKeyboardButton("📢 𝐂𝐇𝐀𝐍𝐍𝐄𝐋", url="https://t.me/FZ_LINK")
    ],
    [
        InlineKeyboardButton("𝐎ᴡɴᴇʀ", url="https://t.me/FZ_CREATOR"),
        InlineKeyboardButton("📢 𝐀ʟʟ 𝐁ᴏᴛs", url="https://t.me/BOT_X_SUPPORT/11")
    ],
    [InlineKeyboardButton("🗑️ Close", callback_data="close")]
])
    await client.send_message(chat_id, text, reply_markup=kb)
    
@app.on_message(filters.command("help"))
async def help_handler(client: Client, message):
    chat_id = message.chat.id
    help_text = (
        "**🛠️ Bot Commands & Usage**\n\n"
        "`/config` – set warn-limit & punishment mode\n"
        "`/free` – whitelist a user (reply or user/id)\n"
        "`/unfree` – remove from whitelist\n"
        "`/freelist` – list all whitelisted users\n\n"
        "**When someone with a URL in their bio posts, I’ll:**\n"
        " 1. ⚠️ Warn them\n"
        " 2. 🔇 Mute if they exceed limit\n"
        " 3. 🔨 Ban if set to ban\n\n"
        "**Use the inline buttons on warnings to cancel or whitelist**"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🗑️ Close", callback_data="close")]
    ])
    await client.send_message(chat_id, help_text, reply_markup=kb)

@app.on_message(filters.group & filters.command("config"))
async def configure(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not await is_admin(client, chat_id, user_id):
        return

    mode, limit, penalty = await get_config(chat_id)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Warn", callback_data="warn")],
        [
            InlineKeyboardButton("Mute ✅" if penalty == "mute" else "Mute", callback_data="mute"),
            InlineKeyboardButton("Ban ✅" if penalty == "ban" else "Ban", callback_data="ban")
        ],
        [InlineKeyboardButton("Close", callback_data="close")]
    ])
    await client.send_message(
        chat_id,
        "**Choose penalty for users with links in bio:**",
        reply_markup=keyboard
    )
    await message.delete()

@app.on_message(filters.group & filters.command("free"))
async def command_free(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not await is_admin(client, chat_id, user_id):
        return

    if message.reply_to_message:
        target = message.reply_to_message.from_user
    elif len(message.command) > 1:
        arg = message.command[1]
        target = await client.get_users(int(arg) if arg.isdigit() else arg)
    else:
        return await client.send_message(chat_id, "**Reply or use /free user or id to whitelist someone.**")

    await add_whitelist(chat_id, target.id)
    await reset_warnings(chat_id, target.id)

    text = f"**✅ {target.mention} has been added to the whitelist**"
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🚫 Unwhitelist", callback_data=f"unwhitelist_{target.id}"),
            InlineKeyboardButton("🗑️ Close", callback_data="close")
        ]
    ])
    await client.send_message(chat_id, text, reply_markup=keyboard)

@app.on_message(filters.group & filters.command("unfree"))
async def command_unfree(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not await is_admin(client, chat_id, user_id):
        return

    if message.reply_to_message:
        target = message.reply_to_message.from_user
    elif len(message.command) > 1:
        arg = message.command[1]
        target = await client.get_users(int(arg) if arg.isdigit() else arg)
    else:
        return await client.send_message(chat_id, "**Reply or use /unfree user or id to unwhitelist someone.**")

    if await is_whitelisted(chat_id, target.id):
        await remove_whitelist(chat_id, target.id)
        text = f"**🚫 {target.mention} has been removed from the whitelist**"
    else:
        text = f"**ℹ️ {target.mention} is not whitelisted.**"

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Whitelist", callback_data=f"whitelist_{target.id}"),
            InlineKeyboardButton("🗑️ Close", callback_data="close")
        ]
    ])
    await client.send_message(chat_id, text, reply_markup=keyboard)

@app.on_message(filters.group & filters.command("freelist"))
async def command_freelist(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not await is_admin(client, chat_id, user_id):
        return

    ids = await get_whitelist(chat_id)
    if not ids:
        await client.send_message(chat_id, "**⚠️ No users are whitelisted in this group.**")
        return

    text = "**📋 Whitelisted Users:**\n\n"
    for i, uid in enumerate(ids, start=1):
        try:
            user = await client.get_users(uid)
            name = f"{user.first_name}{(' ' + user.last_name) if user.last_name else ''}"
            text += f"{i}: {name} [`{uid}`]\n"
        except:
            text += f"{i}: [User not found] [`{uid}`]\n"

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🗑️ Close", callback_data="close")]])
    await client.send_message(chat_id, text, reply_markup=keyboard)

@app.on_callback_query()
async def callback_handler(client: Client, callback_query):
    data = callback_query.data
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    if not await is_admin(client, chat_id, user_id):
        return await callback_query.answer("❌ You are not administrator", show_alert=True)

    if data == "close":
        return await callback_query.message.delete()

    if data == "back":
        mode, limit, penalty = await get_config(chat_id)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Warn", callback_data="warn")],
            [
                InlineKeyboardButton("Mute ✅" if penalty=="mute" else "Mute", callback_data="mute"),
                InlineKeyboardButton("Ban ✅" if penalty=="ban" else "Ban", callback_data="ban")
            ],
            [InlineKeyboardButton("Close", callback_data="close")]
        ])
        await callback_query.message.edit_text("**Choose penalty for users with links in bio:**", reply_markup=kb)
        return await callback_query.answer()

    if data == "warn":
        _, selected_limit, _ = await get_config(chat_id)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"3 ✅" if selected_limit==3 else "3", callback_data="warn_3"),
             InlineKeyboardButton(f"4 ✅" if selected_limit==4 else "4", callback_data="warn_4"),
             InlineKeyboardButton(f"5 ✅" if selected_limit==5 else "5", callback_data="warn_5")],
            [InlineKeyboardButton("Back", callback_data="back"), InlineKeyboardButton("Close", callback_data="close")]
        ])
        return await callback_query.message.edit_text("**Select number of warns before penalty:**", reply_markup=kb)

    if data in ["mute", "ban"]:
        await update_config(chat_id, penalty=data)
        mode, limit, penalty = await get_config(chat_id)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Warn", callback_data="warn")],
            [
                InlineKeyboardButton("Mute ✅" if penalty=="mute" else "Mute", callback_data="mute"),
                InlineKeyboardButton("Ban ✅" if penalty=="ban" else "Ban", callback_data="ban")
            ],
            [InlineKeyboardButton("Close", callback_data="close")]
        ])
        await callback_query.message.edit_text("**Punishment selected:**", reply_markup=kb)
        return await callback_query.answer()

    if data.startswith("warn_"):
        count = int(data.split("_")[1])
        await update_config(chat_id, limit=count)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"3 ✅" if count==3 else "3", callback_data="warn_3"),
             InlineKeyboardButton(f"4 ✅" if count==4 else "4", callback_data="warn_4"),
             InlineKeyboardButton(f"5 ✅" if count==5 else "5", callback_data="warn_5")],
            [InlineKeyboardButton("Back", callback_data="back"), InlineKeyboardButton("Close", callback_data="close")]
        ])
        await callback_query.message.edit_text(f"**Warning limit set to {count}**", reply_markup=kb)
        return await callback_query.answer()

    if data.startswith(("unmute_", "unban_")):
        action, uid = data.split("_")
        target_id = int(uid)
        user = await client.get_chat(target_id)
        name = f"{user.first_name}{(' ' + user.last_name) if user.last_name else ''}"
        try:
            if action == "unmute":
                await client.restrict_chat_member(chat_id, target_id, ChatPermissions(can_send_messages=True))
            else:
                await client.unban_chat_member(chat_id, target_id)
            await reset_warnings(chat_id, target_id)
            msg = f"**{name} (`{target_id}`) has been {'unmuted' if action=='unmute' else 'unbanned'}**."

            kb = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("Whitelist ✅", callback_data=f"whitelist_{target_id}"),
                    InlineKeyboardButton("🗑️ Close", callback_data="close")
                ]
            ])
            await callback_query.message.edit_text(msg, reply_markup=kb)
        
        except errors.ChatAdminRequired:
            await callback_query.message.edit_text(f"I don't have permission to {action} users.")
        return await callback_query.answer()

    if data.startswith("cancel_warn_"):
        target_id = int(data.split("_")[-1])
        await reset_warnings(chat_id, target_id)
        user = await client.get_chat(target_id)
        full_name = f"{user.first_name}{(' ' + user.last_name) if user.last_name else ''}"
        mention = f"[{full_name}](tg://user?id={target_id})"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Whitelist✅", callback_data=f"whitelist_{target_id}"),
             InlineKeyboardButton("🗑️ Close", callback_data="close")]
        ])
        await callback_query.message.edit_text(f"**✅ {mention} [`{target_id}`] has no more warnings!**", reply_markup=kb)
        return await callback_query.answer()

    if data.startswith("whitelist_"):
        target_id = int(data.split("_")[1])
        await add_whitelist(chat_id, target_id)
        await reset_warnings(chat_id, target_id)
        user = await client.get_chat(target_id)
        full_name = f"{user.first_name}{(' ' + user.last_name) if user.last_name else ''}"
        mention = f"[{full_name}](tg://user?id={target_id})"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🚫 Unwhitelist", callback_data=f"unwhitelist_{target_id}"),
             InlineKeyboardButton("🗑️ Close", callback_data="close")]
        ])
        await callback_query.message.edit_text(f"**✅ {mention} [`{target_id}`] has been whitelisted!**", reply_markup=kb)
        return await callback_query.answer()

    if data.startswith("unwhitelist_"):
        target_id = int(data.split("_")[1])
        await remove_whitelist(chat_id, target_id)
        user = await client.get_chat(target_id)
        full_name = f"{user.first_name}{(' ' + user.last_name) if user.last_name else ''}"
        mention = f"[{full_name}](tg://user?id={target_id})"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Whitelist✅", callback_data=f"whitelist_{target_id}"),
             InlineKeyboardButton("🗑️ Close", callback_data="close")]
        ])
        await callback_query.message.edit_text(f"**❌ {mention} [`{target_id}`] has been removed from whitelist.**", reply_markup=kb)
        return await callback_query.answer()

@app.on_message(filters.group)
async def check_bio(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if await is_admin(client, chat_id, user_id) or await is_whitelisted(chat_id, user_id):
        return

    user = await client.get_chat(user_id)
    bio = user.bio or ""
    full_name = f"{user.first_name}{(' ' + user.last_name) if user.last_name else ''}"
    mention = f"[{full_name}](tg://user?id={user_id})"

    if URL_PATTERN.search(bio):
        try:
            await message.delete()
        except errors.MessageDeleteForbidden:
            return await message.reply_text("Please grant me delete permission.")

        mode, limit, penalty = await get_config(chat_id)
        if mode == "warn":
            count = await increment_warning(chat_id, user_id)
            warning_text = (
                "**🚨 Warning Issued** 🚨\n\n"
                f"👤 **User:** {mention} `[{user_id}]`\n"
                "❌ **Reason:** URL found in bio\n"
                f"⚠️ **Warning:** {count}/{limit}\n\n"
                "**Notice: Please remove any links from your bio.**"
            )
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cancel Warning", callback_data=f"cancel_warn_{user_id}"),
                 InlineKeyboardButton("✅ Whitelist", callback_data=f"whitelist_{user_id}")],
                [InlineKeyboardButton("🗑️ Close", callback_data="close")]
            ])
            sent = await message.reply_text(warning_text, reply_markup=keyboard)
            if count >= limit:
                try:
                    if penalty == "mute":
                        await client.restrict_chat_member(chat_id, user_id, ChatPermissions())
                        kb = InlineKeyboardMarkup([[InlineKeyboardButton("Unmute ✅", callback_data=f"unmute_{user_id}")]])
                        await sent.edit_text(f"**{user_name} has been 🔇 muted for [Link In Bio].**", reply_markup=kb)
                    else:
                        await client.ban_chat_member(chat_id, user_id)
                        kb = InlineKeyboardMarkup([[InlineKeyboardButton("Unban ✅", callback_data=f"unban_{user_id}")]])
                        await sent.edit_text(f"**{user_name} has been 🔨 banned for [Link In Bio].**", reply_markup=kb)
                
                except errors.ChatAdminRequired:
                    await sent.edit_text(f"**I don't have permission to {penalty} users.**")
        else:
            try:
                if mode == "mute":
                    await client.restrict_chat_member(chat_id, user_id, ChatPermissions())
                    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Unmute", callback_data=f"unmute_{user_id}")]])
                    await message.reply_text(f"{user_name} has been 🔇 muted for [Link In Bio].", reply_markup=kb)
                else:
                    await client.ban_chat_member(chat_id, user_id)
                    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Unban", callback_data=f"unban_{user_id}")]])
                    await message.reply_text(f"{user_name} has been 🔨 banned for [Link In Bio].", reply_markup=kb)
            except errors.ChatAdminRequired:
                return await message.reply_text(f"I don't have permission to {mode} users.")
    else:
        await reset_warnings(chat_id, user_id)

if __name__ == "__main__":
# ================= Broadcast Command ===================
@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast(client, message):
    args = message.text.split(maxsplit=2)
    if len(args) < 2:
        return await message.reply_text("Usage: /broadcast <msg>\n/broadcast -pin <msg>\n/broadcast -user <msg>")

    flag = None
    if args[1] in ["-pin", "-user"]:
        if len(args) < 3:
            return await message.reply_text("Usage: /broadcast -pin <msg> or /broadcast -user <msg>")
        flag = args[1]
        broadcast_text = args[2]
    else:
        broadcast_text = " ".join(args[1:])

    cur.execute("SELECT user_id FROM users")
    rows = cur.fetchall()
    total_users = 0
    sent_users = 0
    pinned_users = 0
    failed_users = 0
    total_groups = 0
    sent_groups = 0
    pinned_groups = 0
    failed_groups = 0

    # Pre-check groups vs users
    for (uid,) in rows:
        try:
            chat = await client.get_chat(uid)
            if chat.type in ("group", "supergroup"):
                total_groups += 1
            else:
                total_users += 1
        except:
            failed_users += 1

    progress_msg = await message.reply_text("📊 🔥ʙʀᴏᴀᴅᴄᴀꜱᴛ ʀᴇꜱᴜʟᴛ🔥\nProcessing...")

    for uid, in rows:
        try:
            chat = await client.get_chat(uid)
            if flag == "-user" and chat.type != "private":
                if chat.type in ("group", "supergroup"):
                    failed_groups += 1
                else:
                    failed_users += 1
                continue

            msg = await client.send_message(uid, broadcast_text)
            if chat.type in ("group", "supergroup"):
                sent_groups += 1
                if flag == "-pin" and await bot_is_admin_with_permissions(client, uid, "can_pin_messages"):
                    try: await msg.pin(disable_notification=True)
                    except: pass
                    pinned_groups += 1
            else:
                sent_users += 1
                if flag == "-pin":
                    try: await client.send_message(uid, "📌 [PINNED]\n" + broadcast_text)
                    pinned_users += 1
        except:
            if chat.type in ("group", "supergroup"):
                failed_groups += 1
            else:
                failed_users += 1

    total_sent = sent_groups + sent_users
    total_failed = failed_groups + failed_users

    final_text = f"""📊 🔥ʙʀᴏᴀᴅᴄᴀꜱᴛ ʀᴇꜱᴜʟᴛ🔥

✨Gʀᴏᴜᴘꜱ:
      » ᴛᴏᴛᴀʟ: {total_groups}
      » ꜱᴇɴᴛ: {sent_groups}
      » ᴘɪɴɴᴇᴅ: {pinned_groups}
      » ꜰᴀɪʟᴇᴅ: {failed_groups}

🥀Uꜱᴇʀꜱ:
      » ᴛᴏᴛᴀʟ: {total_users}
      » ꜱᴇɴᴛ: {sent_users}
      » ᴘɪɴɴᴇᴅ: {pinned_users}
      » ꜰᴀɪʟᴇᴅ: {failed_users}

🎉ᴛᴏᴛᴀʟ ꜱᴇɴᴛ: {total_sent}
🤒ᴛᴏᴛᴀʟ ꜰᴀɪʟᴇᴅ: {total_failed}"""

    await progress_msg.edit_text(final_text)


# ================= Forward Broadcast (/fgcast) ===================
@app.on_message(filters.command("fgcast") & filters.user(OWNER_ID))
async def fgcast(client, message):
    args = message.text.split(maxsplit=2)
    if len(args) < 2:
        return await message.reply_text("Usage: /fgcast <msg_id|reply> [-pin/-user]")

    flag = None
    fg_message = None

    if message.reply_to_message:
        fg_message = message.reply_to_message
        if len(args) >= 2 and args[1] in ["-pin", "-user"]:
            flag = args[1]
    else:
        if args[1].isdigit():
            try:
                fg_message = await client.get_messages(message.chat.id, int(args[1]))
            except:
                return await message.reply_text("Message not found")
        if len(args) >= 3 and args[1] in ["-pin", "-user"]:
            flag = args[1]

    if not fg_message:
        return await message.reply_text("Reply to a message or provide message ID")

    cur.execute("SELECT user_id FROM users")
    rows = cur.fetchall()

    total_users = 0
    sent_users = 0
    pinned_users = 0
    failed_users = 0
    total_groups = 0
    sent_groups = 0
    pinned_groups = 0
    failed_groups = 0

    # Pre-check
    for (uid,) in rows:
        try:
            chat = await client.get_chat(uid)
            if chat.type in ("group", "supergroup"):
                total_groups += 1
            else:
                total_users += 1
        except:
            failed_users += 1

    progress_msg = await message.reply_text("📊 🔥ʙʀᴏᴀᴅᴄᴀꜱᴛ ʀᴇꜱᴜʟᴛ🔥\nProcessing...")

    for uid, in rows:
        try:
            chat = await client.get_chat(uid)
            if flag == "-user" and chat.type != "private":
                if chat.type in ("group", "supergroup"):
                    failed_groups += 1
                else:
                    failed_users += 1
                continue

            fwd_msg = await fg_message.forward(uid)
            if chat.type in ("group", "supergroup"):
                sent_groups += 1
                if flag == "-pin" and await bot_is_admin_with_permissions(client, uid, "can_pin_messages"):
                    try: await fwd_msg.pin(disable_notification=True)
                    except: pass
                    pinned_groups += 1
            else:
                sent_users += 1
                if flag == "-pin":
                    try: await client.send_message(uid, "📌 [PINNED] Forwarded message below:")
                    pinned_users += 1
        except:
            if chat.type in ("group", "supergroup"):
                failed_groups += 1
            else:
                failed_users += 1

    total_sent = sent_groups + sent_users
    total_failed = failed_groups + failed_users

    final_text = f"""📊 🔥ʙʀᴏᴀᴅᴄᴀꜱᴛ ʀᴇꜱᴜʟᴛ🔥

✨Gʀᴏᴜᴘꜱ:
      » ᴛᴏᴛᴀʟ: {total_groups}
      » ꜱᴇɴᴛ: {sent_groups}
      » ᴘɪɴɴᴇᴅ: {pinned_groups}
      » ꜰᴀɪʟᴇᴅ: {failed_groups}

🥀Uꜱᴇʀꜱ:
      » ᴛᴏᴛᴀʟ: {total_users}
      » ꜱᴇɴᴛ: {sent_users}
      » ᴘɪɴɴᴇᴅ: {pinned_users}
      » ꜰᴀɪʟᴇᴅ: {failed_users}

🎉ᴛᴏᴛᴀʟ ꜱᴇɴᴛ: {total_sent}
🤒ᴛᴏᴛᴀʟ ꜰᴀɪʟᴇᴅ: {total_failed}"""

    await progress_msg.edit_text(final_text)
