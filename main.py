import os
import json
import psycopg2
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import RPCError
from pyrogram import idle
from openai import OpenAI

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
DATABASE_URL = os.environ.get("DATABASE_URL")

START_VIDEO = "https://files.catbox.moe/zbu2ql.mp4"
START_LOG_VIDEO = "https://files.catbox.moe/mr83rj.mp4"

# -------- LOGGER SETTINGS -------- #
LOGGER_ID = -1003272813374  # <-- put your correct log group/channel ID
START_LOG_IMAGE = "https://files.catbox.moe/z5tnz1.jpg"
# --------------------------------- #

bot = Client(
    "chatbot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

client_ai = OpenAI(api_key=OPENAI_API_KEY)

conn = psycopg2.connect(DATABASE_URL, sslmode="require")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS memory (
    user_id BIGINT PRIMARY KEY,
    messages TEXT
)
""")
conn.commit()

# ---------------- LOGGER FUNCTIONS ---------------- #

async def send_boot_log():
    try:
        me = await bot.get_me()
        await bot.send_photo(
            chat_id=LOGGER_ID,
            photo=START_LOG_IMAGE,
            caption=(
                f"<blockquote><u><b>» {me.mention} ʙᴏᴛ ʙᴏᴏᴛᴇᴅ 🚀</b></u></blockquote>\n\n"
                f"<b>ɪᴅ :</b> <code>{me.id}</code>\n"
                f"<b>ɴᴀᴍᴇ :</b> {me.first_name}\n"
                f"<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{me.username}"
            ),
            parse_mode="html"
        )
    except Exception as e:
        print(f"[Logger error] Could not send boot log: {e}")

async def send_user_log(user):
    try:
        await bot.send_video(
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
    except Exception as e:
        print(f"[Logger error] Could not send user log: {e}")

async def send_group_add_log(chat):
    try:
        await bot.send_video(
            chat_id=LOGGER_ID,
            video=START_LOG_VIDEO,
            caption=(
                f"<blockquote><u><b>» ʙᴏᴛ ᴀᴅᴅᴇᴅ ɪɴ ɢʀᴏᴜᴘ 🔥</b></u></blockquote>\n\n"
                f"<b>ɢʀᴏᴜᴘ :</b> {chat.title}\n"
                f"<b>ɪᴅ :</b> <code>{chat.id}</code>"
            ),
            parse_mode="html"
        )
    except Exception as e:
        print(f"[Logger error] Could not send group add log: {e}")

# ---------------- MEMORY ---------------- #

def get_memory(user_id):
    cur.execute("SELECT messages FROM memory WHERE user_id=%s", (user_id,))
    row = cur.fetchone()
    if row:
        return json.loads(row[0])
    return []

def save_memory(user_id, messages):
    cur.execute("""
    INSERT INTO memory (user_id, messages)
    VALUES (%s, %s)
    ON CONFLICT (user_id)
    DO UPDATE SET messages = EXCLUDED.messages
    """, (user_id, json.dumps(messages)))
    conn.commit()

async def generate_reply(user_id, text):
    memory = get_memory(user_id)
    memory.append({"role": "user", "content": text})

    response = client_ai.chat.completions.create(
        model="gpt-4o-mini",
        messages=memory,
        temperature=0.7,
    )

    reply = response.choices[0].message.content
    memory.append({"role": "assistant", "content": reply})
    save_memory(user_id, memory)

    return reply

# ---------------- START COMMAND ---------------- #

@bot.on_message(filters.command("start"))
async def start_handler(client, message):
    user = message.from_user

    # ---- USER START LOG ---- #
    await send_user_log(user)

    text = (
        f"ʜᴇʏ {user.mention} 👋\n\n"
        "ɪ ᴀᴍ ᴀ ɢᴘᴛ ʟᴇᴠᴇʟ ᴀɪ ᴄʜᴀᴛʙᴏᴛ 🤖✨\n"
        "ɪ ʀᴇᴍᴇᴍʙᴇʀ ᴏᴜʀ ᴄᴏɴᴠᴇʀꜱᴀᴛɪᴏɴꜱ 🧠💾\n\n"
        "ᴊᴜꜱᴛ ꜱᴇɴᴅ ᴀ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ꜱᴛᴀʀᴛ ᴄʜᴀᴛᴛɪɴɢ 🚀"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "✦ ᴧᴅᴅ ϻє ᴛσ ɢʀσᴜᴘ ➕👥✨",
            url=f"https://t.me/{(await client.get_me()).username}?startgroup=true"
        )],
        [
            InlineKeyboardButton("✦ ʟσɢꜱ 📜✨", url=f"https://t.me/yukieee_03"),
            InlineKeyboardButton("✦ σᴡηєʀ 👑✨", url=f"https://t.me/cyber_github")
        ],
        [
            InlineKeyboardButton("✦ ˹ ɪɴꜰɪɴɪᴛʏ ✘ ɴᴇᴛᴡᴏʀᴋ˼ 🎧  🚫🔥", url=f"https://t.me/dark_musictm")
        ]
    ])

    await message.reply(
        f"{text}\n\n<a href='{START_VIDEO}'>๏ ɪ ᴡᴀɴɴᴀ ʙᴇ ʏᴏᴜʀꜱ ♡ 🌷</a>",
        reply_markup=keyboard,
    )

# ---------------- GROUP ADD LOG ---------------- #

@bot.on_message(filters.new_chat_members)
async def bot_added(client, message):
    for member in message.new_chat_members:
        me = await bot.get_me()
        if member.id == me.id:
            await send_group_add_log(message.chat)

# ---------------- CHAT HANDLER ---------------- #

@bot.on_message(filters.text & ~filters.command(["start"]))
async def chat_handler(client, message):
    reply = await generate_reply(message.from_user.id, message.text)
    await message.reply_text(reply)

# ---------------- RUN WITH BOOT LOG ---------------- #

async def main():
    await bot.start()
    await send_boot_log()
    print("Bot Started")
    await idle()
    await bot.stop()

if __name__ == "__main__":
    bot.run(main())
