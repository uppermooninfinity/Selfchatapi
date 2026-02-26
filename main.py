import os
import json
import psycopg2
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from openai import OpenAI

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
DATABASE_URL = os.environ.get("DATABASE_URL")

START_VIDEO = "https://files.catbox.moe/zbu2ql.mp4"

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
        reply_markup=keyboard
    )


# ---------------- CHAT HANDLER ---------------- #

@bot.on_message(filters.text & ~filters.command(["start"]))
async def chat_handler(client, message):
    reply = await generate_reply(message.from_user.id, message.text)
    await message.reply_text(reply)


bot.run()
