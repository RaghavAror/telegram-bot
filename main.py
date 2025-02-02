import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
from config import Config
from handlers import messages
import sys
import asyncio

# Fix for Windows event loop policy
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def main() -> None:
    """Run the bot."""
    application = ApplicationBuilder().token(Config.TELEGRAM_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", messages.start))
    application.add_handler(CommandHandler("help", messages.help_command))
    application.add_handler(MessageHandler(filters.CONTACT, messages.handle_contact))
    application.add_handler(CommandHandler("websearch", messages.handle_websearch))
    application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, messages.handle_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, messages.handle_message))

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()