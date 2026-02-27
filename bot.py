import os
import uuid
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)
from services.tts_service import text_to_speech
from utils.limits import can_use
from config import BOT_TOKEN, FREE_DAILY_LIMIT, MAX_TEXT_LENGTH

# Load environment variables
load_dotenv()

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎙 Welcome to AI Voice Bot!\n\n"
        "Send any text and I’ll convert it to speech.\n\n"
        f"Free users: {FREE_DAILY_LIMIT} conversions per day."
    )

# Handle incoming text
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text.strip()

    # Check text length
    if len(user_text) > MAX_TEXT_LENGTH:
        await update.message.reply_text(
            f"⚠️ Max {MAX_TEXT_LENGTH} characters allowed."
        )
        return

    # Check daily limit
    if not can_use(user_id, FREE_DAILY_LIMIT):
        await update.message.reply_text(
            "🚫 Daily limit reached.\n\nUpgrade to premium for unlimited access."
        )
        return

    await update.message.reply_text("🎙 Converting to speech...")

    file_name = f"{uuid.uuid4()}.mp3"

    try:
        audio_path = await text_to_speech(user_text, file_name)

        # Send as voice note (cleaner in Telegram)
        with open(audio_path, "rb") as audio_file:
            await update.message.reply_voice(voice=audio_file)

    except Exception as e:
        logging.error(f"Error generating speech: {e}")
        await update.message.reply_text("❌ Something went wrong.")

    finally:
        if os.path.exists(file_name):
            os.remove(file_name)

# Async main for Python 3.14 + PTB 21.6
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logging.info("Bot is running...")

    # Start bot
    await app.start()
    await app.updater.start_polling()
    await app.updater.wait_closed()
    await app.stop()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())