from pyrogram import Client, filters
from pyrogram.errors import RPCError

# ====== EDIT THESE TWO ======

START_VIDEO = "https://files.catbox.moe/zbu2ql.mp4"
START_LOG_VIDEO = "https://files.catbox.moe/mr83rj.mp4"
# -------- LOGGER SETTINGS -------- #
LOGGER_ID = -1003272813374  # <-- apna log group id
START_LOG_IMAGE = "https://files.catbox.moe/z5tnz1.jpg" # 
# ============================


async def send_boot_log(app: Client):
    try:
        await app.send_photo(
            chat_id=LOGGER_ID,
            photo=START_LOG_IMAGE,
            has_spoiler=True,
            caption=(
                f"<blockquote><u><b>» {app.mention} ʙᴏᴛ ʙᴏᴏᴛᴇᴅ ᴏɴʟɪɴᴇ 🚀</b></u></blockquote>\n\n"
                f"<b>ɪᴅ :</b> <code>{app.id}</code>\n"
                f"<b>ɴᴀᴍᴇ :</b> {app.name}\n"
                f"<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{app.username}\n"
                f"<b>ᴘʟᴀᴛғᴏʀᴍ :</b> VPS / Heroku\n"
            ),
            parse_mode="html"
        )
    except RPCError:
        pass


async def send_user_start_log(client: Client, message):
    try:
        user = message.from_user
        await client.send_video(
            chat_id=LOGGER_ID,
            video=START_LOG_VIDEO,
            caption=(
                f"<blockquote><u><b>» ɴᴇᴡ ᴜsᴇʀ sᴛᴀʀᴛᴇᴅ 🐺</b></u></blockquote>\n\n"
                f"<b>ɴᴀᴍᴇ :</b> {user.mention}\n"
                f"<b>ɪᴅ :</b> <code>{user.id}</code>\n"
                f"<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{user.username if user.username else 'None'}"
            ),
            parse_mode="html"
        )
    except RPCError:
        pass


async def send_group_add_log(client: Client, message):
    try:
        chat = message.chat
        await client.send_video(
            chat_id=LOGGER_ID,
            video=START_LOG_VIDEO,
            caption=(
                f"<blockquote><u><b>» ʙᴏᴛ ᴀᴅᴅᴇᴅ ɪɴ ɢʀᴏᴜᴘ 🔥</b></u></blockquote>\n\n"
                f"<b>ɢʀᴏᴜᴘ :</b> {chat.title}\n"
                f"<b>ɪᴅ :</b> <code>{chat.id}</code>\n"
                f"<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{chat.username if chat.username else 'Private'}"
            ),
            parse_mode="html"
        )
    except RPCError:
        pass
