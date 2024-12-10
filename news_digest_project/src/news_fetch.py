import os
import redis
import asyncio
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
import openai

# Настройки
API_ID = '26085699'
API_HASH = 'd1b7a0f11173040508d4e214b3189bc3'
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
CHANNELS = ['@buhtourbiz', '@portierdenuit']  # Укажите каналы для сбора новостей
OPENAI_API_KEY = 'YOUR_OPENAI_API_KEY'  # Замените на ваш OpenAI API Key

# Инициализация Redis
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

# Инициализация клиента Telegram
client = TelegramClient('session_name', API_ID, API_HASH)

async def fetch_news(channel):
    entity = await client.get_entity(channel)
    
    # Получение истории сообщений
    history = await client(GetHistoryRequest(
        peer=entity,
        limit=10,  # Количество сообщений для получения
        offset_date=None,
        offset_id=0,
        add_offset=0,
        hash=0
    ))

    for message in history.messages:
        if message.message:
            print(f"Получено сообщение: {message.message}")  # Отладочное сообщение
            # Сохранение сообщения в Redis
            redis_client.lpush('news_posts', message.message)

async def summarize_news():
    # Получение сообщений из Redis
    news_posts = redis_client.lrange('news_posts', 0, -1)
    summaries = []

    openai.api_key = OPENAI_API_KEY
    
    for post in news_posts:
        response = openai.ChatCompletion.create(
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
    await client.start()  # Запускаем клиент только один раз
    # Сбор новостей из всех указанных каналов
    await asyncio.gather(*(fetch_news(channel) for channel in CHANNELS))
    await summarize_news()
    await client.disconnect()  # Отключаем клиент после завершения работы

if __name__ == '__main__':
    asyncio.run(main())
