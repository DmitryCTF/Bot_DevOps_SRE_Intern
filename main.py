import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, PeerFloodError

load_dotenv()
api_id_raw = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
target_chat = os.getenv("TARGET_CHAT", "me")
source_chats_raw = os.getenv("SOURCE_CHATS", "")

if api_id_raw is None:
    raise RuntimeError("Не найден API_ID. Проверь файл .env")

if api_hash is None:
    raise RuntimeError("Не найден API_HASH. Проверь файл .env")

def normalize_chat_source(source):
    source = source.strip()

    if source.startswith("https://t.me/"):
        source = source.replace("https://t.me/", "")

    if source.startswith("http://t.me/"):
        source = source.replace("http://t.me/", "")

    if source.startswith("t.me/"):
        source = source.replace("t.me/", "")

    if not source.startswith("@"):
        source = "@" + source

    return source

api_id = int(api_id_raw)
session_name = "telegram_session"
source_chats = [
    normalize_chat_source(chat)
    for chat in source_chats_raw.split(",")
    if chat.strip()
]
client = TelegramClient(session_name, api_id, api_hash)

def find_keywords(post_text, keywords):
    post_text_lower = post_text.lower()

    found_keywords = []

    for keyword in keywords:
        keyword_lower = keyword.lower()

        if keyword_lower in post_text_lower:
            found_keywords.append(keyword)

    return found_keywords

def format_found_post_message(post_text, found_keywords, source):
    keywords_text = ", ".join(found_keywords)

    message = (
        "🔎 Найден подходящий пост\n\n"
        f"Источник: {source}\n"
        f"Ключевые слова: {keywords_text}\n\n"
        f"Текст:\n{post_text}"
    )

    return message

async def process_post(post_text, source):
    found_keywords = find_keywords(post_text, keywords)

    if not found_keywords:
        print(f"Пост из источника {source} пропущен")
        return

    telegram_message = format_found_post_message(post_text, found_keywords, source)

    try:
        await client.send_message(target_chat, telegram_message)

        print(f"Пост из источника {source} отправлен в {target_chat}")
        print(f"Найденные слова: {found_keywords}")

        await asyncio.sleep(5)

    except FloodWaitError as error:
        print(f"Telegram просит подождать {error.seconds} секунд")
        await asyncio.sleep(error.seconds)

    except PeerFloodError:
        print("Telegram временно ограничил отправку сообщений. Останови бота и попробуй позже.")

@client.on(events.NewMessage(chats=source_chats))
async def new_message_handler(event):
    post_text = event.raw_text

    if not post_text:
        return

    chat = await event.get_chat()

    source = getattr(chat, "title", None)

    if source is None:
        source = getattr(chat, "username", "Неизвестный источник")

    await process_post(post_text, source)

keywords = [
    "DevOps",
    "SRE",
    "Системный Администратор",
    "Intern",
    "Екатеринбург",
    "Прикладной администратор",
    "Администрирование",
    "Системный администратор",
    "Сис. админ",
    "Сис админ"
]
async def main():
    me = await client.get_me()

    print("Успешно подключились к Telegram")
    print(f"Имя: {me.first_name}")
    print(f"Username: {me.username}")
    print(f"ID аккаунта: {me.id}")
    print(f"Целевой чат: {target_chat}")
    print(f"Количество источников: {len(source_chats)}")
    print(f"Источники: {source_chats}")
    print("Бот запущен и ждёт новые посты...")

with client:
    client.loop.run_until_complete(main())
    client.run_until_disconnected()