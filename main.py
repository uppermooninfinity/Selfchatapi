import os
import json
import psycopg2
import requests
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ---------------- ENV VARIABLES ---------------- #

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROK_API_KEY = os.environ.get("GROK_API_KEY")
DATABASE_URL = os.environ.get("DATABASE_URL")

START_VIDEO = "https://files.catbox.moe/ehcs2v.mp4"
START_LOG_VIDEO = "https://files.catbox.moe/ehcs2v.mp4"

LOGGER_ID = -1003272813374
START_LOG_IMAGE = "https://files.catbox.moe/z5tnz1.jpg"

# ---------------- BOT INIT ---------------- #

bot = Client(
    "chatbot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ---------------- DATABASE ---------------- #

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
                f"<b>» {me.mention} Bot Booted 🚀</b>\n\n"
                f"<b>ID:</b> <code>{me.id}</code>\n"
                f"<b>Name:</b> {me.first_name}\n"
                f"<b>Username:</b> @{me.username}"
            ),
            parse_mode="html"
        )
    except Exception as e:
        print(f"[Logger error] {e}")

async def send_user_log(user):
    try:
        await bot.send_video(
            chat_id=LOGGER_ID,
            video=START_LOG_VIDEO,
            caption=(
                f"<b>» New User Started 🐺</b>\n\n"
                f"<b>Name:</b> {user.mention}\n"
                f"<b>ID:</b> <code>{user.id}</code>\n"
                f"<b>Username:</b> @{user.username if user.username else 'None'}"
            ),
            parse_mode="html"
        )
    except Exception as e:
        print(f"[Logger error] {e}")

async def send_group_add_log(chat):
    try:
        await bot.send_video(
            chat_id=LOGGER_ID,
            video=START_LOG_VIDEO,
            caption=(
                f"<b>» Bot Added In Group 🔥</b>\n\n"
                f"<b>Group:</b> {chat.title}\n"
                f"<b>ID:</b> <code>{chat.id}</code>"
            ),
            parse_mode="html"
        )
    except Exception as e:
        print(f"[Logger error] {e}")

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

# ---------------- SPECIAL TRIGGERS ---------------- #

TRIGGER_RESPONSES = {
    "hi": "Hey there 👋✨ How can I help you today?",
    "hello": "Hello 🌸✨ Nice to see you here!",
    "hui": "Huiii 😆 kya chal raha hai?",
    "hi eivya": "Hii 💖 I'm always here for you!",
    "jay shree ram": "🚩 Jai Shree Ram 🙏✨",
    "jai shree ram": "🚩 Jai Shree Ram 🙏✨"
}

def check_trigger(text):
    text_lower = text.lower().strip()
    return TRIGGER_RESPONSES.get(text_lower)

# ---------------- GROK CHAT FUNCTION ---------------- #

async def generate_reply(user_id, text):
    memory = get_memory(user_id)
    memory.append({"role": "user", "content": text})

    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "grok-2-latest",
        "messages": memory,
        "temperature": 0.7
    }

    try:
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )

        result = response.json()
        reply = result["choices"][0]["message"]["content"]

    except Exception as e:
        print("Grok API Error:", e)
        reply = "⚠️ AI is temporarily unavailable. Try again later."

    memory.append({"role": "assistant", "content": reply})
    save_memory(user_id, memory)

    return reply

# ---------------- START COMMAND ---------------- #

@bot.on_message(filters.command("start"))
async def start_handler(client, message):
    user = message.from_user
    await send_user_log(user)

    text = (
        f"<blockquote>ʜᴇʏ {message.from_user.mention} 👋</blockquote>\n\n"
         "<blockquote>ɪ ᴀᴍ ᴀ ɢʀᴏǫ-ᴘᴏᴡᴇʀᴇᴅ ᴀɪ ᴄʜᴀᴛʙᴏᴛ ⚡\n"
         "ʙᴜɪʟᴛ ғᴏʀ sᴍᴀʀᴛ, ғᴀsᴛ ᴀɴᴅ ᴀᴄᴄᴜʀᴀᴛᴇ ʀᴇsᴘᴏɴsᴇs 💡</blockquote>\n\n"
         "<blockquote>✨ ᴀsᴋ ᴍᴇ ᴀɴʏᴛʜɪɴɢ — ᴄᴏᴅɪɴɢ, ᴋɴᴏᴡʟᴇᴅɢᴇ, ɢᴇɴᴇʀᴀʟ ᴄʜᴀᴛs\n"
         "🚀 ᴊᴜsᴛ sᴇɴᴅ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ sᴛᴀʀᴛ ᴄʜᴀᴛᴛɪɴɢ\n"
         "🔥 ғᴀsᴛ ʀᴇᴘʟɪᴇs • sᴍᴀʀᴛ ʟᴏɢɪᴄ • ᴘᴏᴡᴇʀғᴜʟ ᴀɪ</blockquote>\n\n"
         "<blockquote>ʟᴇᴛ’s ᴄʀᴇᴀᴛᴇ sᴏᴍᴇᴛʜɪɴɢ ᴀᴍᴀᴢɪɴɢ ᴛᴏɢᴇᴛʜᴇʀ 🩵</blockquote>\n"
         "</blockquote>🛡️ ɪ ᴄᴀɴ sᴍᴀʀᴛʟʏ ᴍᴏɴɪᴛᴏʀ ᴀɴᴅ ᴘʀᴏᴛᴇᴄᴛ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴄʜᴀᴛ ғʀᴏᴍ ɴsғᴡ ᴀɴᴅ ᴜɴᴡᴀɴᴛᴇᴅ ᴄᴏɴᴛᴇɴᴛ 🌷✨</blockquote>"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "ღ ᴀᴅᴅ ᴍᴇ ღ",
            url=f"https://t.me/{(await client.get_me()).username}?startgroup=true"
        )]
    ])

    await message.reply(
        f"{text}\n\n<a href='{START_VIDEO}'>ᴍᴀᴅᴇ ᴡɪᴛʜ ʟᴏᴠᴇ ғᴏʀ ᴍʏ ᴀᴍᴀᴢɪɴɢ ᴜsᴇʀs 🩵✨</a>",
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

    trigger_reply = check_trigger(message.text)

    if trigger_reply:
        await message.reply_text(trigger_reply)
        return

    reply = await generate_reply(message.from_user.id, message.text)
    await message.reply_text(reply)

# ---------------- RUN ---------------- #

async def main():
    await bot.start()
    await send_boot_log()
    print("Bot Started")
    await idle()
    await bot.stop()

if __name__ == "__main__":
    bot.run(main())
