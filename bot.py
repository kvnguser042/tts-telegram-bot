import os
import uuid
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from services.tts_service import text_to_speech
from utils.limits import can_use
from config import BOT_TOKEN, FREE_DAILY_LIMIT, MAX_TEXT_LENGTH

# Load environment variables
load_dotenv()

# Logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎙 Welcome to AI Voice Bot!\nSend text and I’ll convert it to speech.\n"
        f"Free users: {FREE_DAILY_LIMIT} conversions per day."
    )

# Handle text messages
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if len(text) > MAX_TEXT_LENGTH:
        await update.message.reply_text(f"⚠️ Max {MAX_TEXT_LENGTH} characters allowed.")
        return

    if not can_use(user_id, FREE_DAILY_LIMIT):
        await update.message.reply_text(
            "🚫 Daily limit reached. Upgrade to premium for unlimited access."
        )
        return

    await update.message.reply_text("🎙 Converting to speech...")

    file_name = f"{uuid.uuid4()}.mp3"
    try:
        audio_path = await text_to_speech(text, file_name)
        with open(audio_path, "rb") as f:
            await update.message.reply_voice(f)
    except Exception as e:
        logging.error(f"Error generating speech: {e}")
        await update.message.reply_text("❌ Something went wrong.")
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)

# --------------------------
# MAIN ENTRY POINT
# --------------------------
if __name__ == "__main__":
    # Build bot application
    app = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logging.info("Bot is running...")

    # ✅ Stable polling on Python 3.14.3
    app.run_polling()