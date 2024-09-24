import inspect
import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from modules.birthdays import check_birthdays
from modules.random_quote import get_random_quote
from modules.beastars_quote import get_beastars_quote
from modules.spotify import find_playlist
from ai import ai_response, clear_history

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_ID = os.getenv("ADMIN_ID")
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
}

# Function to run a module
async def run_module(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
        if result:
            await update.message.reply_text(result)
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
    response = "Things I can do: \n/" + " /".join(modules.keys())
    await update.message.reply_text(response)
    
async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    clear_history()
    response = "Cleared history"
    await update.message.reply_text(response)
    

# Function to handle incoming messages and generate AI responses
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    print(f"Received message: {user_message}")
    
    ai_reply = ai_response(user_message)
    await update.message.reply_text(ai_reply)
    print(f"Bot response: {ai_reply}")

def main() -> None:
    # Create the Application and pass it your bot's token
    application = ApplicationBuilder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("clear", clear))

    # Add a single handler for all module commands
    application.add_handler(CommandHandler(list(modules.keys()), run_module))

    # Add message handler for AI responses
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Schedule birthday checks
    scheduler.add_job(modules["birthdays"], 'cron', hour=10, minute=0)

    # Start the scheduler
    scheduler.start()

    # Run the bot until the user presses Ctrl-C
    print("Polling...")
    application.run_polling()

if __name__ == "__main__":
    main()
