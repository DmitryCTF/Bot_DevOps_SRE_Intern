import keyword
import os
from dotenv import load_dotenv
from telethon import TelegramClient, events

load_dotenv()
api_id_raw = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
target_chat = os.getenv("TARGET_CHAT", "me")

if api_id_raw is None:
    raise RuntimeError("Не найден API_ID. Проверь файл .env")

if api_hash is None:
    raise RuntimeError("Не найден API_HASH. Проверь файл .env")

api_id = int(api_id_raw)
session_name = "telegram_session"
client = TelegramClient(session_name, api_id, api_hash)
async def check_telegram_connection():
    me = await client.get_me()

    print("Успешно подключились к Telegram")
    print(f"Имя: {me.first_name}")
    print(f"Username: {me.username}")
    print(f"ID аккаунта: {me.id}")

    await client.send_message(target_chat, "Это тестовое сообщение из Python.")
    print(f"Отправлено в {target_chat}")

def find_keywords(post_text, keywords):
    post_text_lower = post_text.lower()

    found_keywords = []

    for keyword in keywords:
        keyword_lower = keyword.lower()

        if keyword_lower in post_text_lower:
            found_keywords.append(keyword)

    return found_keywords


post_text = "Ищем devops sre инженера в команду"

keywords = [
    "DevOps",
    "SRE",
    "Системный Администратор",
    "Intern",
    "Екатеринбург",
]

found_keywords = find_keywords(post_text, keywords)

if found_keywords:
    print("Ключевые слова найдены")
    print(f"Найденные слова: {found_keywords}")
else:
    print("Ключевые слова не найдены")

with client:
    client.loop.run_until_complete(check_telegram_connection())