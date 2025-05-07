from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember, WebAppInfo
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from flask import Flask, request
from threading import Thread
import os
import logging

# Setup logging untuk debugging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask('')

@app.route('/')
def home():
    return "Bot sedang berjalan."

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = Update.de_json(request.get_json(), bot)
        dp.process_update(update)
        return "OK"
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return "Error", 500

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# /start command
def start(update: Update, context: CallbackContext):
    try:
        help_text = ("📌 *Senarai Arahan Tersedia:*\n"
                     "/play - Pilih game secara button\n"
                     "/snakegame - Main Snake Game dalam group\n"
                     "/memorymatch - Main Memory Match dalam group\n"
                     "/help - Lihat semua arahan")
        update.message.reply_text(help_text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error in start: {e}")
        update.message.reply_text("Ralat berlaku. Sila cuba lagi.")

# /play command
def play(update: Update, context: CallbackContext):
    try:
        keyboard = [[
            InlineKeyboardButton(
                "🎮 Memory Match",
                web_app=WebAppInfo(url="https://ten-important-velociraptor.glitch.me"))
        ],
                    [
                        InlineKeyboardButton(
                            "🐍 Snake Game",
                            web_app=WebAppInfo(url="https://breezy-narrow-busby.glitch.me"))
                    ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Pilih permainan yang anda mahu mainkan:",
                                  reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error in play: {e}")
        update.message.reply_text("Ralat berlaku. Sila cuba lagi.")

# Semak jika bot admin
def is_bot_admin(update: Update, context: CallbackContext) -> bool:
    try:
        chat = update.effective_chat
        if chat.type not in ["group", "supergroup", "channel"]:
            update.message.reply_text(
                "Arahan ini hanya boleh digunakan dalam group atau channel.")
            return False
        bot_member: ChatMember = context.bot.get_chat_member(
            chat.id, context.bot.id)
        if bot_member.status not in ["administrator", "creator"]:
            update.message.reply_text(
                "Saya perlu menjadi admin dalam group ini untuk berfungsi.")
            return False
        return True
    except Exception as e:
        logger.error(f"Error in is_bot_admin: {e}")
        update.message.reply_text("Ralat semasa memeriksa status admin. Sila pastikan bot mempunyai kebenaran yang diperlukan.")
        return False

# /snakegame command
def snakegame(update: Update, context: CallbackContext):
    if not is_bot_admin(update, context):
        return

    try:
        keyboard = [[
            InlineKeyboardButton("🐍 Main Snake Game",
                                web_app=WebAppInfo(url="https://breezy-narrow-busby.glitch.me"))
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Klik untuk bermain Snake Game!",
                                  reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error in snakegame: {e}")
        update.message.reply_text("Ralat berlaku. Sila cuba lagi.")

# /memorymatch command
def memorymatch(update: Update, context: CallbackContext):
    if not is_bot_admin(update, context):
        return

    try:
        keyboard = [[
            InlineKeyboardButton("🧠 Main Memory Match",
                                web_app=WebAppInfo(url="https://ten-important-velociraptor.glitch.me"))
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Klik untuk bermain Memory Match!",
                                  reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error in memorymatch: {e}")
        update.message.reply_text("Ralat berlaku. Sila cuba lagi.")

# /help command
def help_command(update: Update, context: CallbackContext):
    try:
        help_text = ("📌 *Senarai Arahan Tersedia:*\n"
                     "/play - Pilih game secara button\n"
                     "/snakegame - Main Snake Game dalam group\n"
                     "/memorymatch - Main Memory Match dalam group\n"
                     "/help - Lihat semua arahan")
        update.message.reply_text(help_text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error in help_command: {e}")
        update.message.reply_text("Ralat berlaku. Sila cuba lagi.")

# Respond bila orang mention bot
def mention_reply(update: Update, context: CallbackContext):
    try:
        text = update.message.text.lower()
        bot_username = f"@{context.bot.username.lower()}"

        if bot_username in text:
            if "snake game" in text:
                keyboard = [[
                    InlineKeyboardButton(
                        "🐍 Main Snake Game",
                        web_app=WebAppInfo(url="https://breezy-narrow-busby.glitch.me"))
                ]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text("Klik di bawah untuk main Snake Game!",
                                          reply_markup=reply_markup)

            elif "memory match" in text:
                keyboard = [[
                    InlineKeyboardButton(
                        "🧠 Main Memory Match",
                        web_app=WebAppInfo(url="https://ten-important-velociraptor.glitch.me"))
                ]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text("Klik di bawah untuk main Memory Match!",
                                          reply_markup=reply_markup)
            else:
                update.message.reply_text(
                    "Saya sedia membantu! Taip /help untuk lihat arahan yang ada.")
    except Exception as e:
        logger.error(f"Error in mention_reply: {e}")
        update.message.reply_text("Ralat berlaku. Sila cuba lagi.")

# Main
def main():
    try:
        TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
        if not TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN tidak ditetapkan dalam environment variable")

        render_url = os.environ.get("RENDER_EXTERNAL_URL")
        if not render_url:
            raise ValueError("RENDER_EXTERNAL_URL tidak ditetapkan dalam environment variable")

        render_url = render_url.replace("https://", "").replace("http://", "")

        global bot, dp
        bot = Bot(TOKEN)
        updater = Updater(TOKEN, use_context=True)
        dp = updater.dispatcher

        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("play", play))
        dp.add_handler(CommandHandler("snakegame", snakegame))
        dp.add_handler(CommandHandler("memorymatch", memorymatch))
        dp.add_handler(CommandHandler("help", help_command))
        dp.add_handler(
            MessageHandler(Filters.text & Filters.entity("mention"),
                           mention_reply))

        keep_alive()

        webhook_url = f"https://{render_url}/webhook"
        logger.info(f"Setting webhook to: {webhook_url}")
        bot.delete_webhook()  # Bersihkan webhook lama jika ada
        response = bot.setWebhook(url=webhook_url)
        if not response:
            logger.error("Webhook setup failed")
            raise Exception("Webhook setup failed")
        else:
            logger.info("Webhook set successfully")

        updater.idle()
    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == '__main__':
    main()
