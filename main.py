from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.constants import ParseMode
from flask import Flask, request
from threading import Thread
import os

app = Flask('')

@app.route('/')
def home():
    return "Bot sedang berjalan."

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = Update.de_json(request.get_json(), application.bot)
        application.process_update(update)
        return "OK"
    except Exception as e:
        print(f"Webhook error: {e}")
        return "Error", 500

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        help_text = ("📌 *Senarai Arahan Tersedia:*\n"
                     "/play - Pilih game secara button\n"
                     "/snakegame - Main Snake Game dalam group\n"
                     "/memorymatch - Main Memory Match dalam group\n"
                     "/help - Lihat semua arahan")
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await update.message.reply_text("Ralat berlaku. Sila cuba lagi.")

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        username = user.username if user.username else f"User_{user.id}"
        keyboard = [[
            InlineKeyboardButton(
                "🎮 Memory Match",
                url=f"https://t.me/QuickPlayGameBot/memorymatch?username={username}")
        ],
                    [
                        InlineKeyboardButton(
                            "🐍 Snake Game",
                            url=f"https://t.me/QuickPlayGameBot/snakegame?username={username}")
                    ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Pilih permainan yang anda mahu mainkan:", reply_markup=reply_markup)
    except Exception as e:
        await update.message.reply_text("Ralat berlaku. Sila cuba lagi.")

async def is_bot_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        chat = update.effective_chat
        if chat.type not in ["group", "supergroup", "channel"]:
            await update.message.reply_text("Arahan ini hanya boleh digunakan dalam group atau channel.")
            return False
        bot_member = await context.bot.get_chat_member(chat.id, context.bot.id)
        if bot_member.status not in ["administrator", "creator"]:
            await update.message.reply_text("Saya perlu menjadi admin dalam group ini untuk berfungsi.")
            return False
        return True
    except Exception as e:
        await update.message.reply_text("Ralat semasa memeriksa status admin. Sila pastikan bot mempunyai kebenaran yang diperlukan.")
        return False

async def snakegame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_bot_admin(update, context):
        return

    try:
        user = update.effective_user
        username = user.username if user.username else f"User_{user.id}"
        game_url = f"https://t.me/QuickPlayGameBot/snakegame?username={username}"
        keyboard = [[
            InlineKeyboardButton("🐍 Main Snake Game", url=game_url)
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Klik untuk bermain Snake Game!", reply_markup=reply_markup)
    except Exception as e:
        await update.message.reply_text("Ralat berlaku. Sila cuba lagi.")

async def memorymatch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_bot_admin(update, context):
        return

    try:
        user = update.effective_user
        username = user.username if user.username else f"User_{user.id}"
        game_url = f"https://t.me/QuickPlayGameBot/memorymatch?username={username}"
        keyboard = [[
            InlineKeyboardButton("🧠 Main Memory Match", url=game_url)
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Klik untuk bermain Memory Match!", reply_markup=reply_markup)
    except Exception as e:
        await update.message.reply_text("Ralat berlaku. Sila cuba lagi.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        help_text = ("📌 *Senarai Arahan Tersedia:*\n"
                     "/play - Pilih game secara button\n"
                     "/snakegame - Main Snake Game dalam group\n"
                     "/memorymatch - Main Memory Match dalam group\n"
                     "/help - Lihat semua arahan")
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await update.message.reply_text("Ralat berlaku. Sila cuba lagi.")

async def mention_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.lower()
        bot_username = f"@{context.bot.username.lower()}"

        if bot_username in text:
            user = update.effective_user
            username = user.username if user.username else f"User_{user.id}"
            if "snake game" in text:
                keyboard = [[
                    InlineKeyboardButton(
                        "🐍 Main Snake Game",
                        url=f"https://t.me/QuickPlayGameBot/snakegame?username={username}")
                ]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text("Klik di bawah untuk main Snake Game!", reply_markup=reply_markup)
            elif "memory match" in text:
                keyboard = [[
                    InlineKeyboardButton(
                        "🧠 Main Memory Match",
                        url=f"https://t.me/QuickPlayGameBot/memorymatch?username={username}")
                ]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text("Klik di bawah untuk main Memory Match!", reply_markup=reply_markup)
            else:
                await update.message.reply_text("Saya sedia membantu! Taip /help untuk lihat arahan yang ada.")
    except Exception as e:
        await update.message.reply_text("Ralat berlaku. Sila cuba lagi.")

async def main():
    try:
        TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
        if not TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN tidak ditetapkan dalam environment variable")

        render_url = os.environ.get("RENDER_EXTERNAL_URL")
        if not render_url:
            raise ValueError("RENDER_EXTERNAL_URL tidak ditetapkan dalam environment variable")

        render_url = render_url.replace("https://", "").replace("http://", "")

        global application
        application = Application.builder().token(TOKEN).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("play", play))
        application.add_handler(CommandHandler("snakegame", snakegame))
        application.add_handler(CommandHandler("memorymatch", memorymatch))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(
            MessageHandler(filters.TEXT & filters.ENTITY("mention"), mention_reply))

        keep_alive()

        webhook_url = f"https://{render_url}/webhook"
        print(f"Setting webhook to: {webhook_url}")
        await application.bot.set_webhook(url=webhook_url)
        print("Webhook set successfully")

        await application.run_polling()
    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
