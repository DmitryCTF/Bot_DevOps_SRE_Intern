import os
import json
import asyncio

from dotenv import load_dotenv
from telethon import TelegramClient, events, utils
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


RECENT_POSTS_LIMIT = 5
SEND_DELAY_SECONDS = 10
PROCESSED_MESSAGES_FILE = "processed_messages.json"


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


def load_processed_messages():
    try:
        with open(PROCESSED_MESSAGES_FILE, "r", encoding="utf-8") as file:
            messages = json.load(file)

        return set(messages)

    except FileNotFoundError:
        return set()

    except json.JSONDecodeError:
        print("Файл processed_messages.json повреждён. Начинаю с пустого списка.")
        return set()


def save_processed_messages():
    with open(PROCESSED_MESSAGES_FILE, "w", encoding="utf-8") as file:
        json.dump(
            sorted(processed_messages),
            file,
            ensure_ascii=False,
            indent=2,
        )


def make_message_key(chat_id, message_id):
    return f"{chat_id}:{message_id}"


api_id = int(api_id_raw)
session_name = "telegram_session"

source_chats = [
    normalize_chat_source(chat)
    for chat in source_chats_raw.split(",")
    if chat.strip()
]

client = TelegramClient(session_name, api_id, api_hash)

processed_messages = load_processed_messages()


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
    "Сис админ",
]


def get_source_name(chat):
    username = getattr(chat, "username", None)

    if username:
        return f"@{username}"

    return getattr(chat, "title", "Неизвестный источник")


def get_post_link(chat, message_id):
    username = getattr(chat, "username", None)

    if not username:
        return None

    return f"https://t.me/{username}/{message_id}"


def find_keywords(post_text, keywords):
    post_text_lower = post_text.lower()

    found_keywords = []

    for keyword in keywords:
        keyword_lower = keyword.lower()

        if keyword_lower in post_text_lower:
            found_keywords.append(keyword)

    return found_keywords


def format_found_post_message(post_text, found_keywords, source, post_link=None):
    keywords_text = ", ".join(found_keywords)

    message = (
        "🔎 Найден подходящий пост\n\n"
        f"Источник: {source}\n"
    )

    if post_link:
        message += f"Ссылка на пост: {post_link}\n"

    message += (
        f"Ключевые слова: {keywords_text}\n\n"
        f"Текст:\n{post_text}"
    )

    return message


async def process_post(post_text, source, post_link=None):
    found_keywords = find_keywords(post_text, keywords)

    if not found_keywords:
        print(f"Пост из источника {source} пропущен")
        return

    telegram_message = format_found_post_message(
        post_text,
        found_keywords,
        source,
        post_link,
    )

    try:
        await client.send_message(target_chat, telegram_message)

        print(f"Пост из источника {source} отправлен в {target_chat}")
        print(f"Найденные слова: {found_keywords}")

        await asyncio.sleep(SEND_DELAY_SECONDS)

    except FloodWaitError as error:
        print(f"Telegram просит подождать {error.seconds} секунд")
        await asyncio.sleep(error.seconds)

    except PeerFloodError:
        print("Telegram временно ограничил отправку сообщений. Останови бота и попробуй позже.")


@client.on(events.NewMessage(chats=source_chats))
async def new_message_handler(event):
    message_key = make_message_key(event.chat_id, event.id)

    if message_key in processed_messages:
        print(f"Дубликат пропущен: {message_key}")
        return

    processed_messages.add(message_key)
    save_processed_messages()

    post_text = event.raw_text

    if not post_text:
        return

    chat = await event.get_chat()
    source = get_source_name(chat)
    post_link = get_post_link(chat, event.id)

    await process_post(post_text, source, post_link)


async def check_recent_posts():
    print(f"Проверяю последние {RECENT_POSTS_LIMIT} постов в источниках...")

    for source_chat in source_chats:
        try:
            chat = await client.get_entity(source_chat)
            source = get_source_name(chat)

            print(f"Проверяю источник: {source}")

            recent_messages = []

            async for message in client.iter_messages(chat, limit=RECENT_POSTS_LIMIT):
                recent_messages.append(message)

            for message in reversed(recent_messages):
                message_chat_id = getattr(message, "chat_id", None)

                if message_chat_id is None:
                    message_chat_id = utils.get_peer_id(chat)

                message_key = make_message_key(message_chat_id, message.id)

                if message_key in processed_messages:
                    print(f"Дубликат пропущен: {message_key}")
                    continue

                processed_messages.add(message_key)
                save_processed_messages()

                post_text = message.raw_text

                if not post_text:
                    continue

                post_link = get_post_link(chat, message.id)

                await process_post(post_text, source, post_link)

        except Exception as error:
            print(f"Не удалось проверить источник {source_chat}: {error}")


async def main():
    me = await client.get_me()

    print("Успешно подключились к Telegram")
    print(f"Имя: {me.first_name}")
    print(f"Username: {me.username}")
    print(f"ID аккаунта: {me.id}")
    print(f"Целевой чат: {target_chat}")
    print(f"Количество источников: {len(source_chats)}")
    print(f"Источники: {source_chats}")

    await check_recent_posts()

    print("Бот запущен и ждёт новые посты...")


with client:
    client.loop.run_until_complete(main())
    client.run_until_disconnected()