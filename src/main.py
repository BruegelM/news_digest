import redis
import asyncio
import openai
from telethon import TelegramClient
from fetch_news import fetch_news

# Настройки
API_ID = '26085699'
API_HASH = 'd1b7a0f11173040508d4e214b3189bc3'
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
CHANNELS = ['@travelline_news', '@russpass_business']  # Укажите каналы для сбора новостей
OPENAI_API_KEY = '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'  # Замените на ваш OpenAI API Key

# Инициализация Redis
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

async def summarize_news():
    # Получение сообщений из Redis
    news_posts = redis_client.lrange('news_posts', 0, -1)
    summaries = []

    openai.api_key = OPENAI_API_KEY
    
    for post in news_posts:
        response = await openai.ChatCompletion.create(  # Добавлено await
            model="gpt-3.5-turbo",  # Используйте правильное имя модели
            messages=[
                {"role": "user", "content": f"Сделай краткое резюме для следующей новости: {post}"}
            ]
        )
        summaries.append(response['choices'][0]['message']['content'])

    # Сохранение резюме в Redis
    redis_client.delete('news_posts')  # Очистить старые посты
    for summary in summaries:
        redis_client.lpush('news_summaries', summary)

async def main():
    client = TelegramClient('session_name', API_ID, API_HASH)
    await client.start()  # Запускаем клиент только один раз
    news_items = []
    
    # Сбор новостей из всех указанных каналов
    for channel in CHANNELS:
        news = await fetch_news(client, channel)  # Передаем client в fetch_news
        news_items.extend(news)  # Добавляем новые сообщения в общий список

    await summarize_news()  # Получаем резюме для всех новостей

    for item in news_items:
        print(f"Оригинал: {item}")  # Печатаем оригинальные сообщения

    await client.disconnect()  # Отключаем клиент после завершения работы

if __name__ == '__main__':
    asyncio.run(main())
