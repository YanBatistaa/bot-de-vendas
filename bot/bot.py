# bot/bot.py

import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler
)
from core.config import TELEGRAM_TOKEN
from bot.handlers import start, show_products, button_handler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING) # Silencia logs excessivos do httpx
logger = logging.getLogger(__name__)

def setup_bot() -> Application:
    """Configura e retorna a aplicação do bot para ser executada posteriormente."""
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^🛍️ Ver Produtos$'), show_products))
    application.add_handler(CallbackQueryHandler(button_handler))

    return application