import os
import requests
import time
import asyncio
from telegram import Bot
from telegram.error import TelegramError
import hashlib

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
URL = os.getenv('URL')
CONTENT_FILE = 'content_hash.txt'

if not URL:
    raise ValueError("Die Umgebungsvariable URL muss gesetzt sein.")

async def send_telegram_message(message):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
    except TelegramError as e:
        print(f"Fehler beim Senden der Nachricht: {e}")

def load_saved_content():
    try:
        with open(CONTENT_FILE, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return None

def save_content(content):
    with open(CONTENT_FILE, 'w', encoding='utf-8') as file:
        file.write(content)

initial_content = load_saved_content()

async def monitor_website():
    global initial_content

    response = requests.get(URL)
    h = hashlib.new('sha256')
    current_content = hashlib.sha256(response.text.encode('utf-8')).hexdigest()

    print(current_content)
    print(URL)

    if initial_content is None:
        save_content(current_content)
        initial_content = current_content

    if current_content != initial_content:
        await send_telegram_message('News: ' + URL)
        save_content(current_content)  # Update the saved content
        initial_content = current_content

if __name__ == "__main__":
    asyncio.run(monitor_website())
