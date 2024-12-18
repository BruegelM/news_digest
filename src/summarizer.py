import os
import redis
import openai
from config import OPENAI_API_KEY
from openai import OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Настройки Redis
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

# Инициализация Redis
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

async def summarize(text):
    """Функция для саммаризации текста с использованием OpenAI API."""
    openai.api_key = OPENAI_API_KEY
    try:
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {"role": "user", "content": f"Сделай краткое изложение следующего текста: {text}"}
            ]
        )
        summary = response['choices'][0]['message']['content']
        return summary
    except Exception as e:
        print(f"Ошибка при вызове OpenAI API: {e}")
        return None

async def process_news():
    """Основная функция для обработки новостных постов."""
    # Получаем новостные посты из Redis
    news_posts = redis_client.lrange('news_posts', 0, -1)  # Получаем все посты из списка
    print("Полученные посты:", news_posts)  # Выводим полученные посты

    summaries = []

    for post in news_posts:
        summary = await summarize(post)  # Саммаризируем каждый пост
        if summary:  # Проверяем, что резюме не равно None
            summaries.append(summary)  # Сохраняем резюме в список

    # Сохраняем резюме в другой список Redis
    redis_client.delete('news_summaries')  # Очистка старого списка
    for summary in summaries:
        redis_client.lpush('news_summaries', summary)  # Добавляем резюме в новый список

if __name__ == '__main__':
    import asyncio
    asyncio.run(process_news())  # Запускаем основную функцию
