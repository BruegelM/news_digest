import redis
from telethon.tl.functions.messages import GetHistoryRequest

# Настройки
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

# Инициализация Redis
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

async def fetch_news(client, channel):
    entity = await client.get_entity(channel)
    
    # Получение истории сообщений
    history = await client(GetHistoryRequest(
        peer=entity,
        limit=10,  # Количество сообщений для получения
        offset_date=None,
        offset_id=0,
        add_offset=0,
        max_id=10,
        min_id=0,
        hash=0
    ))

    messages = []
    for message in history.messages:
        if message.message:
            print(f"Получено сообщение: {message.message}")  # Отладочное сообщение
            messages.append(message.message)
            # Сохранение сообщения в Redis
            redis_client.lpush('news_posts', message.message)
    
    return messages  # Возвращаем список сообщений
