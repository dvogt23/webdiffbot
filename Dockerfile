FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY webpage_monitor.py .

ARG TELEGRAM_BOT_TOKEN
ENV TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_API_TOKEN
ARG CHAT_ID
ENV CHAT_ID=YOUR_CHAT_ID
ARG URL
ENV URL=URL

CMD ["python", "webpage_monitor.py"]
