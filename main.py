import keyword

from telethon import TelegramClient, events


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