from telethon import TelegramClient

# Конфигурация Telegram
API_ID = '26085699'
API_HASH = 'd1b7a0f11173040508d4e214b3189bc3'
CHANNEL_USERNAME = 'travel_digest'

# Инициализация клиента Telegram
client = TelegramClient('session_name', API_ID, API_HASH)

async def fetch_news():
    await client.start()
    async for message in client.iter_messages(CHANNEL_USERNAME, limit=10):
        if message.text:
            yield message.text
