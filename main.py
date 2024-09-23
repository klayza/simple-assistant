import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from modules.birthdays import check_birthdays
from modules.random_quote import get_random_quote
from modules.beastars_quote import get_beastars_quote

# Load environment variables
load_dotenv()

TOKEN = os.getenv("TELEGRAM_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_ID = os.getenv("ADMIN_ID")
USER_ID = ADMIN_ID

# Initialize the scheduler
scheduler = AsyncIOScheduler()

# Module registry
modules = {
    "birthdays": check_birthdays,
    "quote": get_random_quote,
    "beastars": get_beastars_quote
}

# Function to run a module
async def run_module(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    command = update.message.text.split()[0][1:]  # Remove the leading '/'
    if command in modules:
        result = modules[command]()
        if result:
            await update.message.reply_text(result)
    else:
        await update.message.reply_text(f"Module '{command}' not found.")

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Yo, I'm your assistant. Run /help to see what I can do.")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Things I can do: \n/" + " /".join(modules.keys()))

# Function to print incoming messages
async def print_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"Received message: {update.message.text}")

def main() -> None:
    # Create the Application and pass it your bot's token
    application = ApplicationBuilder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))

    # Add a single handler for all module commands
    application.add_handler(CommandHandler(list(modules.keys()), run_module))

    # Add message handler to print all incoming messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, print_message))

    # Schedule birthday checks
    scheduler.add_job(modules["birthdays"], 'cron', hour=10, minute=0)

    # Start the scheduler
    scheduler.start()

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()