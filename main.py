import asyncio
import inspect
import os
import logging
import random
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from modules.birthdays import check_birthdays
from modules.manager import check_done, final_check
from modules.random_quote import get_random_quote
from modules.beastars_quote import get_beastars_quote
from modules.spotify import find_playlist
from ai import ai_response, clear_history

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_ID = os.getenv("ADMIN_ID")
CHAT_ID = os.getenv("CHAT_ID")
USER_ID = ADMIN_ID

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.ERROR)
logger = logging.getLogger(__name__)

# Initialize the scheduler
scheduler = AsyncIOScheduler()

# Module registry
modules = {
    "birthdays": check_birthdays,
    "quote": get_random_quote,
    "beastars": get_beastars_quote,
    "spotify": find_playlist,
    "check_done": check_done,
    "final_check": final_check,
}

# Create the Application and pass it your bot's token
application = ApplicationBuilder().token(TOKEN).build()

# Function to check if the user is admin
def is_admin(update: Update) -> bool:
    return str(update.message.from_user.id) == ADMIN_ID

# Function to run a module
async def run_module(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update):
        await update.message.reply_text("Get lost fool, you ain't the admin.")
        return

    command = update.message.text.split()[0][1:]  # Remove the leading '/'
    params = update.message.text.split(" ", 1)[1:] # All text after first space (as a list)

    if command in modules:
        func = modules[command]

        # Use inspect to find the function's signature
        sig = inspect.signature(func)
        num_params = len(sig.parameters)

        try:
            if num_params == 0:
                # Call function without parameters
                result = func()
            else:
                # Call function with parameters if provided
                if params:
                    result = func(*params)
                else:
                    await update.message.reply_text(f"Command /{command} requires parameters.")
                    return
        except Exception as e:
            await update.message.reply_text(f"Error executing command /{command}: {str(e)}")
            return

        # Reply with result if valid
        if result != None:
            await update.message.reply_text(result, parse_mode="HTML")
            logger.info(f"Bot response to /{command}: {result}")
        else:
            await update.message.reply_text(f"Command /{command} did not return a result.")
    else:
        await update.message.reply_text(f"Module {command} not found.")
        logger.info(f"Module {command} not found.")
        
        
# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    response = "Yo, I'm your assistant. Run /help to see what I can do."
    await update.message.reply_text(response)

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update):
        await update.message.reply_text("Get lost fool, you ain't the admin.")
        return

    response = "Things I can do: \n/" + " /".join(modules.keys())
    await update.message.reply_text(response)
    
async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update):
        return

    clear_history()
    response = "Cleared history"
    await update.message.reply_text(response)
    

# Function to handle incoming messages and generate AI responses
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update):
        await update.message.reply_text("Get lost fool, you ain't the admin.")
        return

    user_message = update.message.text
    print(f"Received message: {user_message}")
    
    ai_reply = ai_response(user_message)
    await update.message.reply_text(ai_reply)
    print(f"Bot response: {ai_reply}")


    
def random_time():
    start_hr = 8
    end_hr = 22
    return f"{random.randrange(start=start_hr, stop=end_hr)}:00"

def do_final_check():
    response = final_check()
    if response:
        application.bot.send_message(chat_id=CHAT_ID, text=response)

# Async function to check jobs
async def check_jobs():
    while True:
        scheduler.run_pending()
        await asyncio.sleep(1)  # Non-blocking sleep

def main():
    application.bot.send_message(chat_id=CHAT_ID, text="Sup yo")

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("clear", clear))
    application.add_handler(CommandHandler(list(modules.keys()), run_module))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Set up the scheduler
    scheduler = AsyncIOScheduler()
    # scheduler.add_job(lambda: print(modules["check_done"]()), 'interval', seconds=1)  
    # scheduler.add_job(lambda: print(modules["final_check"]()), 'interval', seconds=20)  
    # scheduler.add_job(lambda: print(modules["check_done"]()), 'cron', hour=23)  
    scheduler.start()

    # Run the bot until the user presses Ctrl-C
    print("Polling...")
    application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())