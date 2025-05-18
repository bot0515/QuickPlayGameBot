from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, Dispatcher, CallbackQueryHandler
from flask import Flask, request, jsonify, render_template_string
from threading import Thread
import os
from telegram import ParseMode
from telegram import Bot
import requests

app = Flask('')

# Global variables to store group info
group_id = None
group_name = None

# HTML template to display group info
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram Group ID Display</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background-color: #f0f0f0;
        }
        .container {
            text-align: center;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        #groupId, #groupName {
            font-size: 24px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Telegram Group Info</h1>
        <p>Group ID will be displayed here:</p>
        <div id="groupId">Waiting for Group ID...</div>
        <p>Group Name will be displayed here:</p>
        <div id="groupName">Waiting for Group Name...</div>
    </div>

    <script>
        async function fetchGroupInfo() {
            const response = await fetch('/get_group_info');
            const data = await response.json();
            document.getElementById('groupId').textContent = data.group_id;
            document.getElementById('groupName').textContent = data.group_name;
        }

        fetchGroupInfo();
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/update_group_info', methods=['POST'])
def update_group_info():
    global group_id, group_name
    data = request.json
    group_id = data.get('group_id')
    group_name = data.get('group_name')
    return jsonify({"status": "success"})

@app.route('/get_group_info', methods=['GET'])
def get_group_info():
    global group_id, group_name
    return jsonify({"group_id": group_id, "group_name": group_name})

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = Update.de_json(request.get_json(), bot)
        dp.process_update(update)
        return "OK"
    except Exception as e:
        print(f"Webhook error: {e}")
        return "Error", 500

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

def start(update: Update, context: CallbackContext):
    try:
        chat = update.effective_chat
        group_id = chat.id
        group_name = chat.title

        # Send group info to Flask server
        response = requests.post('http://127.0.0.1:8080/update_group_info', json={'group_id': group_id, 'group_name': group_name})
        if response.status_code != 200:
            print("Failed to send group info to server.")

        help_text = ("📌 *Senarai Arahan Tersedia:*\n"
                     "/play - Pilih game secara button\n"
                     "/snakegame - Main Snake Game dalam group\n"
                     "/memorymatch - Main Memory Match dalam group\n"
                     "/help - Lihat semua arahan")
        update.message.reply_text(help_text, parse_mode="Markdown")
    except Exception as e:
        update.message.reply_text("Ralat berlaku. Sila cuba lagi.")

def play(update: Update, context: CallbackContext):
    try:
        keyboard = [[
            InlineKeyboardButton(
                "🎮 Memory Match",
                url="https://t.me/QuickPlayGameBot/memorymatch")
        ],
                    [
                        InlineKeyboardButton(
                            "🐍 Snake Game",
                            url="https://t.me/QuickPlayGameBot/snakegame")
                    ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Pilih permainan yang anda mahu mainkan:",
                                  reply_markup=reply_markup)
    except Exception as e:
        update.message.reply_text("Ralat berlaku. Sila cuba lagi.")

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
        update.message.reply_text("Ralat semasa memeriksa status admin. Sila pastikan bot mempunyai kebenaran yang diperlukan.")
        return False

def snakegame(update: Update, context: CallbackContext):
    if not is_bot_admin(update, context):
        return

    try:
        chat = update.effective_chat
        group_id = chat.id
        group_name = chat.title

        keyboard = [[
            InlineKeyboardButton("🐍 Main Snake Game",
                                url=f"https://t.me/QuickPlayGameBot/snakegame?group_id={group_id}&group_name={group_name}")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Klik untuk bermain Snake Game!",
                                  reply_markup=reply_markup)
    except Exception as e:
        update.message.reply_text("Ralat berlaku. Sila cuba lagi.")

def memorymatch(update: Update, context: CallbackContext):
    if not is_bot_admin(update, context):
        return

    try:
        keyboard = [[
            InlineKeyboardButton("🧠 Main Memory Match",
                                url="https://t.me/QuickPlayGameBot/memorymatch")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Klik untuk bermain Memory Match!",
                                  reply_markup=reply_markup)
    except Exception as e:
        update.message.reply_text("Ralat berlaku. Sila cuba lagi.")

def help_command(update: Update, context: CallbackContext):
    try:
        help_text = ("📌 *Senarai Arahan Tersedia:*\n"
                     "/play - Pilih game secara button\n"
                     "/snakegame - Main Snake Game dalam group\n"
                     "/memorymatch - Main Memory Match dalam group\n"
                     "/help - Lihat semua arahan")
        update.message.reply_text(help_text, parse_mode="Markdown")
    except Exception as e:
        update.message.reply_text("Ralat berlaku. Sila cuba lagi.")

def mention_reply(update: Update, context: CallbackContext):
    try:
        text = update.message.text.lower()
        bot_username = f"@{context.bot.username.lower()}"

        if bot_username in text:
            if "snake game" in text:
                chat = update.effective_chat
                group_id = chat.id
                group_name = chat.title

                keyboard = [[
                    InlineKeyboardButton(
                        "🐍 Main Snake Game",
                        url=f"https://t.me/QuickPlayGameBot/snakegame?group_id={group_id}&group_name={group_name}")
                ]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text("Klik di bawah untuk main Snake Game!",
                                          reply_markup=reply_markup)

            elif "memory match" in text:
                keyboard = [[
                    InlineKeyboardButton(
                        "🧠 Main Memory Match",
                        url="https://t.me/QuickPlayGameBot/memorymatch")
                ]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text("Klik di bawah untuk main Memory Match!",
                                          reply_markup=reply_markup)
            else:
                update.message.reply_text(
                    "Saya sedia membantu! Taip /help untuk lihat arahan yang ada.")
    except Exception as e:
        update.message.reply_text("Ralat berlaku. Sila cuba lagi.")

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
        print(f"Setting webhook to: {webhook_url}")
        response = bot.setWebhook(url=webhook_url)
        if not response:
            print("Webhook setup failed")
        else:
            print("Webhook set successfully")

        updater.idle()
    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == '__main__':
    main()
