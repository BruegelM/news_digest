import redis
import asyncio
import openai
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest  # Импортируем GetHistoryRequest
from fetch_news import fetch_news
from config import API_HASH, PHONE_NUMBER, API_ID
from config import OPENAI_API_KEY

# Настройки
API_ID = API_ID
API_HASH = API_HASH
PHONE_NUMBER = PHONE_NUMBER
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
CHANNELS = ['@travelline_news', '@russpass_business', '@b2bostrovok', 
            '@smartway_today', '@portierdenuit', '@today1520', 
            '@travelstartups', '@hotel_geek', '@travelline_news', 
            '@komandirovki_onetwotrip', '@hotbot_blog', '@bnovonews', 
            '@travelhub_pro', '@buhtourbiz']  # Укажите каналы для сбора новостей

# Инициализация Redis
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

async def summarize_news():
    # Получение сообщений из Redis
    news_posts = redis_client.lrange('news_posts', 0, -1)
    summaries = []

    openai.api_key = OPENAI_API_KEY
    
    for post in news_posts:
        response = await openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
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
        if news is None:  # Проверка на None
            news = []  # Заменяем None на пустой список
        news_items.extend(news)  # Добавляем новые сообщения в общий список

    await summarize_news()  # Получаем резюме для всех новостей

    for item in news_items:
        print(f"Оригинал: {item}")  # Печатаем оригинальные сообщения

    await client.disconnect()  # Отключаем клиент после завершения работы

async def fetch_news(client, channel):
    entity = await client.get_entity(channel)
    
    # Получение истории сообщений
    history = await client(GetHistoryRequest(
        peer=entity,
        limit=10,  # Количество сообщений для получения
        offset_date=None,
        offset_id=0,
        add_offset=0,
        max_id=0,  # Установите в 0, чтобы не ограничивать выборку
        min_id=0,
        hash=0
    ))

    messages = []
    print(f"Получено {len(history.messages)} сообщений из канала {channel}")
    for message in history.messages:
        if message.message:
            print(f"Получено сообщение: {message.message}")  # Отладочное сообщение
            messages.append(message.message)
            # Сохранение сообщения в Redis
            redis_client.lpush('news_posts', message.message)

    return messages  # Возвращаем все сообщения после цикла

if __name__ == '__main__':
    asyncio.run(main())
