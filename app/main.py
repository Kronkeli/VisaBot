import logging
import os
import random
import re
from dotenv import load_dotenv
from telegram import Update, Chat, ChatPermissions, Bot
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, ConversationHandler, filters
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
ACTIVE_ID = 1
ACTIVE_QUESTION = ""
ACTIVE_ANSWER = ""
IS_BOT_ACTIVE = False
ACTIVE_CHAT_ID = ""
ADMINS = []

# For adding questions
QUESTIONS_STATE = 1

# Cursor for database operations
CURSOR = conn.cursor()


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def check_answer(guess):
    return guess.lower() == ACTIVE_ANSWER.lower()

def update_question_from_db():
    global ACTIVE_ID
    global ACTIVE_QUESTION
    global ACTIVE_ANSWER
    CURSOR
    
    try:
        CURSOR.execute("""SELECT * FROM quizzes WHERE id = %s""", (ACTIVE_ID,))
        result_row = CURSOR.fetchone()
        print(str(result_row))

        ACTIVE_QUESTION = result_row[1]
        ACTIVE_ANSWER = result_row[2]
    except:
        logging.warning("Aktiivista kyssäriä ei voitu asettaa. Syynä luultavasti tyhjä taulu.")

def get_admins_from_db():
    global ADMINS
    CURSOR.execute("""SELECT username FROM admins""")
    results = CURSOR.fetchall()
    admins_list = []
    for row in results:
        admins_list.append(row[0])
    ADMINS = admins_list
    logging.info("Adminit päivitetty.")
    print(f"adminit: {ADMINS}")

def get_all_questions_from_db():
    CURSOR.execute("""SELECT * FROM quizzes""")
    results = CURSOR.fetchall()
    result_formatted = f""
    for row in results:
        result_formatted += f"{str(row)} \n"
    
    return result_formatted

def reset_all_questions_from_db():
    CURSOR.execute("""TRUNCATE TABLE quizzes""")
    CURSOR.execute("""ALTER SEQUENCE quizzes_id_seq RESTART""")
    conn.commit()

def add_question_to_db(question, answer):
    CURSOR.execute("""
        INSERT INTO quizzes (question, answer) VALUES (%s, %s);
    """,
    (question.strip(), answer.strip()))
    conn.commit()
    return True

def reset_id():
    global ACTIVE_ID
    ACTIVE_ID = 1

def add_id():
    global ACTIVE_ID
    # Ettei mene yli
    CURSOR.execute("""SELECT MAX(id) FROM quizzes""")
    result_row = CURSOR.fetchone()
    max_id = result_row[0]
    
    if ACTIVE_ID < max_id:
        ACTIVE_ID += 1
        return True
    else:
        return False

def dec_id():
    global ACTIVE_ID
    # Ettei mene ali
    if (ACTIVE_ID > 1):
        ACTIVE_ID -= 1
        return True
    else:
        return False

async def set_bot_status(state):
    if state:
        # await Bot.set_chat_permissions(chat_id=ACTIVE_CHAT_ID, permissions=ChatPermissions(can_send_messages=True))
        logging.info("Kaikennäköinen viestintä on sallittu.")
    else:    
        # await Bot.set_chat_permissions(chat_id=ACTIVE_CHAT_ID, permissions=ChatPermissions(can_send_messages=False))
        logging.info("Kaikennäköinen viestintä on kielletty.")

def check_admin(username):
    CURSOR.execute("""SELECT * FROM admins""")
    results = CURSOR.fetchall()
    for row in results:
        if row[0] == username:
            return True
    return False

def store_question(question_string):
    logging.info("Starting to parse question text...")
    splitted = question_string.split('---')
    if len(splitted) == 2:
        logging.info("Splitattu, ja koitetaan tallettaa muodossa kysymys: '{splitted[0]}', ja vastaus: '{splitted[1]}'")
        if add_question_to_db(splitted[0], splitted[1]):
            return True
    else:
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, MORO talk to me!")

async def activate_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Activate chat message permissions and print the ACTIVE question
    global ACTIVE_QUESTION
    await set_bot_status(True)
    await context.bot.send_message(chat_id=ACTIVE_CHAT_ID, text="Aloitetaan kysymys:")
    await context.bot.send_message(chat_id=ACTIVE_CHAT_ID, text=f"Kysymys on: \n{ACTIVE_QUESTION}")

async def deactivate_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Deactivate chat message permissions
    await set_bot_status(False)
    await context.bot.send_message(chat_id=ACTIVE_CHAT_ID, text="Odotetaan uutta kysymystä...")

async def set_active_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ACTIVE_CHAT_ID
    ACTIVE_CHAT_ID = update.effective_chat.id
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Tämä chätti on nyt pyhitetty botille.")

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lähettää aktiivisen kysymyksen."""
    update_question_from_db()
    if ACTIVE_CHAT_ID != "":
        await context.bot.send_message(chat_id=ACTIVE_CHAT_ID, text=f"Kysymys on: \n{ACTIVE_QUESTION}")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Aktiivista chattia ei ole asetettu.")

async def send_all_questions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    questions = get_all_questions_from_db()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Aktiiviset kyssärit ja vastaukset: \n{questions}")

async def reset_questions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reset_all_questions_from_db()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Kaikki kysymykset resetattu.")

async def start_adding_questions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await context.bot.send_message(chat_id=update.effective_chat.id, 
                                   text=f"Nyt tehtaillaan kyssäreitä. Anna kyssärit (1/viesti) muodossa \nKysymys 1? --- Vastaus 1 \nLopeta keräys komennolla /stop.")
    return QUESTIONS_STATE

async def add_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store question sent by user."""
    try:
        if store_question(update.message.text):
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Kyssäri (ehkä) jopa tallennettu. Katsotaas.")
            questions = get_all_questions_from_db()
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Aktiiviset kyssärit ja vastaukset: \n{questions}")
        else:
            print("Kyssäriä ei tallennettu. Lokin päällä lokki.")

    except:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Tapahtui jokin virhe kyssärin tallennuksessa.")

    return QUESTIONS_STATE    

async def stop_adding_questions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Nyt on tehtailtu kyssäreitä.")
    return ConversationHandler.END

async def send_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lähettää aktiivisen vastauksen."""
    if ACTIVE_CHAT_ID != "":
        await context.bot.send_message(chat_id=ACTIVE_CHAT_ID, text=f"Aktiivinen vastaus on: \n{ACTIVE_ANSWER}")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Aktiivista chattia ei ole asetettu.")

async def send_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lähettää aktiivisen id:n"""
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Aktiivinen id on  nyt: {ACTIVE_ID}")

async def nullify_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Nollaa aktiivisen idn."""
    reset_id()
    global ACTIVE_ID
    update_question_from_db()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ID:tä nollattu ja se on nyt: {ACTIVE_ID}")

async def increase_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lisää aktiivista id:tä."""
    global ACTIVE_ID
    if add_id():
        update_question_from_db()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ID:tä lisätty ja se on nyt: {ACTIVE_ID}")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ID:tä EI lisätty ja se on vielä: {ACTIVE_ID}")

async def decrease_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Vähentää aktiviista id:tä."""
    global ACTIVE_ID
    if dec_id():
        update_question_from_db()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ID:tä vähennetty ja se on nyt: {ACTIVE_ID}")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"ID:tä EI vähennetty ja se on vielä: {ACTIVE_ID}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Checks if the answer is the same as the active answer"""
    guess = update.message.text
    correctness = random.randint(50,100)
    if (check_answer(guess)):
        await update.message.reply_text(f"OIKEIN!!! ({correctness}% todennäköisyydellä)")
        await context.bot.send_message(chat_id=ACTIVE_CHAT_ID, text=f"Oikea vastaushan oli: {ACTIVE_ANSWER}. Todennäköisyys: 100%." )
        
        # After (a likely) correct answer set the chat message permissions to false.
        await set_bot_status(False)
    else:
        await update.message.reply_text("Nyt meni väärin..")


if __name__ == '__main__':
    TOKEN = os.environ['TG_TOKEN']
    application = ApplicationBuilder().token(TOKEN).build()

    # Get the admin names
    get_admins_from_db()
    
    ### ADMIN COMMANDOS ###
    activate_bot_handler = CommandHandler('activate', activate_bot)
    deactivate_bot_handler = CommandHandler('deactivate', deactivate_bot)
    set_active_chat_handler = CommandHandler('set_active_chat', set_active_chat)
    start_handler = CommandHandler('start', start)
    send_question_handler = CommandHandler('send_question', send_question)
    send_all_questions_handler = CommandHandler('send_questions', send_all_questions)
    reset_all_questions_handler = CommandHandler('reset_questions', reset_questions)
    send_answer_handler = CommandHandler('send_answer', send_answer)
    send_id_handler = CommandHandler('send_id', send_id)
    reset_id_handler = CommandHandler('reset_id', nullify_id)
    add_id_handler = CommandHandler('increase_id', increase_id)
    dec_id_handler = CommandHandler('decrease_id', decrease_id)
    # For adding questions
    questions_handler = ConversationHandler(
        entry_points=[CommandHandler('add_questions', start_adding_questions)],
        states={
            QUESTIONS_STATE: [
                MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("stop")), add_question),
            ],
        },
        fallbacks=[CommandHandler('stop', stop_adding_questions)]
    )

    application.add_handler(start_handler)
    application.add_handler(activate_bot_handler)
    application.add_handler(deactivate_bot_handler)
    application.add_handler(set_active_chat_handler)
    application.add_handler(send_question_handler)
    application.add_handler(send_all_questions_handler)
    application.add_handler(reset_all_questions_handler)
    application.add_handler(send_answer_handler)
    application.add_handler(send_id_handler)
    application.add_handler(reset_id_handler)
    application.add_handler(add_id_handler)
    application.add_handler(dec_id_handler)
    application.add_handler(questions_handler)

    application.add_handler(MessageHandler(None, handle_message))

    update_question_from_db()

    application.run_polling()