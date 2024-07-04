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

DEFAULT_IGNORE = (' ', '\\ ')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
INTERVALL = os.getenv('INTERVALL')
URL = os.getenv('URL').split()
IGNORE = tuple(os.getenv('IGNORE').split()) + DEFAULT_IGNORE if os.getenv('IGNORE') else DEFAULT_IGNORE

if not URL:
    raise ValueError("You have to set URL env var.")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("You have to set TELEGRAM_BOT_TOKEN env var.")

if not CHAT_ID:
    raise ValueError("You have to set CHAT_ID env var.")

async def send_telegram_message(message):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    except TelegramError as e:
        print(f"Couldnt send message: {e}")

def load_saved_content(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return None

def save_content(content, file_name):
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(content)

async def check_urls():
    for url in URL:
        CONTENT_FILE = hashlib.sha256(url.encode('utf-8')).hexdigest()
        initial_content = load_saved_content(CONTENT_FILE)
        response = requests.get(url)
        content = markdownify(response.text, heading_style="ATX")
        current_content = os.linesep.join([s for s in content.splitlines() if s and not s.startswith(IGNORE)])

        if initial_content is None:
            save_content(current_content, CONTENT_FILE)
            initial_content = current_content

        if current_content != initial_content:
            NEW_CONTENT = CONTENT_FILE + '.new'
            save_content(current_content, NEW_CONTENT)
            diff = subprocess.run(['diff', CONTENT_FILE, NEW_CONTENT], stdout=subprocess.PIPE)
            message = 'News: ' + url + '\n\n' + '```diff\n' + diff.stdout.decode("utf-8") + '\n```'
            # print(message)
            await send_telegram_message(message)
            save_content(current_content, CONTENT_FILE)
            subprocess.run(['rm', NEW_CONTENT])
            initial_content = current_content

def monitor_website():
    print("I..." + INTERVALL)
    if INTERVALL:
        while True:
            asyncio.run(check_urls())
            time.sleep(int(INTERVALL))
            print("Waiting..." + INTERVALL)
    else:
        asyncio.run(check_urls())

if __name__ == "__main__":
    monitor_website()
