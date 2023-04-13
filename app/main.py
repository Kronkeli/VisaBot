import logging
import os
import random
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler
import psycopg2

load_dotenv()

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

# Some global variables
ACTIVE_ID = 0
ACTIVE_QUESTION = "Mikä on neljä numeroissa?"
ACTIVE_ANSWER = "4"

# Cursor for database operations
CURSOR = conn.cursor()


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def check_answer(guess):
    return guess == ACTIVE_ANSWER

def query_question():
    global ACTIVE_ID
    global ACTIVE_QUESTION
    global ACTIVE_ANSWER
    global CURSOR
    
    CURSOR.execute("""SELECT * FROM quizzes WHERE id = %s""", (ACTIVE_ID,))
    result_row = CURSOR.fetchone()
    print(str(result_row))

    ACTIVE_QUESTION = result_row(1)
    ACTIVE_ANSWER = result_row(2)

def reset_id():
    global ACTIVE_ID
    ACTIVE_ID = 0

def add_id():
    global ACTIVE_ID
    ACTIVE_ID += 1

def dec_id():
    global ACTIVE_ID
    ACTIVE_ID -= 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, MORO talk to me!")

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lähettää aktiivisen kysymyksen."""
    await update.message.reply_text(f"Kysymys on: {ACTIVE_QUESTION}")

async def send_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lähettää aktiivisen vastauksen."""
    await update.message.reply_text(f"Aktiivinen vastaus on: {ACTIVE_ANSWER}")

async def nullify_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Nollaa aktiivisen idn."""
    reset_id()
    global ACTIVE_ID
    await update.message.reply_text(f"ID:tä nollattu ja se on nyt: {ACTIVE_ID}")

async def increase_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lisää aktiivista id:tä."""
    add_id()
    global ACTIVE_ID
    await update.message.reply_text(f"ID:tä lisätty ja se on nyt: {ACTIVE_ID}")

async def decrease_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Vähentää aktiviista id:tä."""
    dec_id()
    global ACTIVE_ID
    await update.message.reply_text(f"ID:tä vähennetty ja se on nyt: {ACTIVE_ID}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Checks if the answer is the same as the active answer"""
    guess = update.message.text
    correctness = random.randint(0,100)
    if (check_answer(guess)):
        await update.message.reply_text(f"OIKEIN!!! ({correctness}% todennäköisyydellä)")
        await update.message.reply_text(f"Oikea vastaushan oli: {ACTIVE_ANSWER}. Todennäköisyys: 100%." )
    else:
        await update.message.reply_text("Nyt meni väärin..")


if __name__ == '__main__':
    TOKEN = os.environ['TG_TOKEN']
    application = ApplicationBuilder().token(TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    send_question_handler = CommandHandler('send_question', send_question)
    send_answer_handler = CommandHandler('send_answer', send_answer)
    reset_id_handler = CommandHandler('send_answer', nullify_id)
    add_id_handler = CommandHandler('send_answer', increase_id)
    dec_id_handler = CommandHandler('send_answer', decrease_id)

    application.add_handler(start_handler)
    application.add_handler(send_question_handler)
    application.add_handler(send_answer_handler)
    application.add_handler(reset_id_handler)
    application.add_handler(add_id_handler)
    application.add_handler(dec_id_handler)

    application.add_handler(MessageHandler(None, handle_message))

    application.run_polling()