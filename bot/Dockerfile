FROM python:3.11
WORKDIR /app
COPY . .
EXPOSE 5000
RUN pip install paramiko psycopg2 python-dotenv python-telegram-bot==13.7
CMD ["python", "tgbot.py"]