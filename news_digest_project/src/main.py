from telethon import TelegramClient
from telethon.sessions import StringSession
import openai
import requests
import json
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import re
import redis
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import asyncio
from news_fetch import fetch_news
from summarizer import summarize

async def main():
    news_items = []
    async for news in fetch_news():
        news_items.append(news)

    for item in news_items:
        summary = await summarize(item)
        print(f"Оригинал: {item}\nРезюме: {summary}\n")

if __name__ == "__main__":
    asyncio.run(main())
