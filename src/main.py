from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from assistant import Assistant
import os
from dotenv import load_dotenv

from utils import from_assistant_message_to_posts

# Load environment variables from .env file
load_dotenv()

# Access environment variables
TELEGRAM_BOT_SECRET_TOKEN = os.getenv("TELEGRAM_BOT_SECRET_TOKEN")

A = Assistant()


app = ApplicationBuilder().token(TELEGRAM_BOT_SECRET_TOKEN).build()
bot = Bot(TELEGRAM_BOT_SECRET_TOKEN)

print("we are ready")


async def post_news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    thread = A.create_thread()
    sample_news = """Hello"""
    A.send_message(
        thread.id,
        sample_news,
    )
    assistant_message = A.get_assistant_response(
        thread_id=thread.id,
    )

    posts = from_assistant_message_to_posts(assistant_message, sample_news)

    for post in posts:
        await bot.send_message(
            text=f"Today's news: \n{post}", chat_id="@uh_TV_neutral_news"
        )

    A.delete_thread(thread.id)


app.add_handler(CommandHandler("post_news", post_news))

app.run_polling()
