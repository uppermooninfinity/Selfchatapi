import os
from fastapi import FastAPI, Request
from pyrogram import Client
from openai import OpenAI
import psycopg2
import json

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
BASE_URL = os.environ.get("BASE_URL")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
DATABASE_URL = os.environ.get("DATABASE_URL")

app = FastAPI()

bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

conn = psycopg2.connect(DATABASE_URL, sslmode="require")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS memory (
    user_id BIGINT PRIMARY KEY,
    messages TEXT
)
""")
conn.commit()


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


@app.on_event("startup")
async def startup():
    await bot.start()
    await bot.set_webhook(f"{BASE_URL}/webhook")


@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_id = data["message"]["from"]["id"]
        text = data["message"].get("text", "")

        reply = await generate_reply(user_id, text)
        await bot.send_message(chat_id, reply)

    return {"status": "ok"}


async def generate_reply(user_id, text):
    memory = get_memory(user_id)

    memory.append({"role": "user", "content": text})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=memory,
        temperature=0.7,
    )

    reply = response.choices[0].message.content
    memory.append({"role": "assistant", "content": reply})

    save_memory(user_id, memory)
    return reply
