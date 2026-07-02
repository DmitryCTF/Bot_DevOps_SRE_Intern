import keyword
import os
from dotenv import load_dotenv
from telethon import TelegramClient, events

load_dotenv()
api_id_raw = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

if api_id_raw is None:
    raise RuntimeError("Не найден API_ID. Проверь файл .env")

if api_hash is None:
    raise RuntimeError("Не найден API_HASH. Проверь файл .env")

api_id = int(api_id_raw)
print("Telegram-настройки успешно загружены")
print(f"API_ID: {api_id}")
print(f"API_HASH длина: {len(api_hash)} символов")

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