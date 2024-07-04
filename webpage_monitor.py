import os
import requests
import time
import asyncio
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError
import hashlib
from markdownify import markdownify
import subprocess

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
URL = os.getenv('URL')
CONTENT_FILE = hashlib.sha256(URL.encode('utf-8')).hexdigest()

IGNORE = ('Copyright', 'Theme:', ' ', '\\ ')

if not URL:
    raise ValueError("You have to set URL env var.")

async def send_telegram_message(message):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode=ParseMode.MARKDOWN)
    except TelegramError as e:
        print(f"Couldnt send message: {e}")

def load_saved_content():
    try:
        with open(CONTENT_FILE, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return None

def save_content(content, file_name):
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(content)

initial_content = load_saved_content()

async def monitor_website():
    global initial_content

    response = requests.get(URL)
    content = markdownify(response.text, heading_style="ATX")
    current_content = os.linesep.join([s for s in content.splitlines() if s and not s.startswith(IGNORE)])

    if initial_content is None:
        save_content(current_content, CONTENT_FILE)
        initial_content = current_content

    if current_content != initial_content:
        NEW_CONTENT = CONTENT_FILE + '.new'
        save_content(current_content, NEW_CONTENT)
        diff = subprocess.run(['diff', CONTENT_FILE, NEW_CONTENT], stdout=subprocess.PIPE)
        message = 'News: ' + URL + '\n\n' + '```diff\n' + diff.stdout.decode("utf-8") + '\n```'
        # print(message)
        await send_telegram_message(message)
        save_content(current_content, CONTENT_FILE)
        subprocess.run(['rm', NEW_CONTENT])
        initial_content = current_content

if __name__ == "__main__":
    asyncio.run(monitor_website())
