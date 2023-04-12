import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import psycopg2

DB_HOST = os.environ['POSTGRES_HOST']
DB_DB = os.environ['POSTGRES_DB']
DB_USER = os.environ['POSTGRES_USER']
DB_PW = os.environ['POSTGRES_PASSWORD']

conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_DB,
    user=DB_USER,
    password=DB_PW
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, MORO talk to me!")

if __name__ == '__main__':
    TOKEN = os.environ['TG_TOKEN']
    application = ApplicationBuilder().token(TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    
    application.run_polling()