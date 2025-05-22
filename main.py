from flask import Flask, request, jsonify, render_template_string
from telegram.ext import Application, CommandHandler
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
import requests
import threading
import re
import os

app = Flask(__name__)

# Global variables
group_id = None
group_name = None

# HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram Group Info</title>
    <style>
        body { font-family: Arial; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background-color: #f0f0f0; }
        .container { text-align: center; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        #groupId, #groupName { font-size: 24px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Telegram Group Info</h1>
        <p>Group ID:</p>
        <div id="groupId">Waiting...</div>
        <p>Group Name:</p>
        <div id="groupName">Waiting...</div>
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

def sanitize_group_name(name):
    if not name:
        return "UnknownGroup"
    return re.sub(r'[^\w]', '', name)

def get_modified_url(chat, base_url):
    if chat.type in ['group', 'supergroup']:
        group_name_clean = sanitize_group_name(chat.title)
        return f"{base_url}?startapp={group_name_clean}&id={chat.id}"
    elif chat.type == 'private':
        return f"{base_url}?startapp={chat.id}"
    return f"{base_url}?startapp=Unknown"

async def start(update, context):
    chat = update.effective_chat
    requests.post('http://127.0.0.1:5000/update_group_info', json={
        'group_id': chat.id,
        'group_name': chat.title
    })

    message = "📌 Senarai Arahan Tersedia:\n" \
              "/play - Pilih game secara button\n" \
              "/snakegame - Main Snake Game\n" \
              "/memorymatch - Main Memory Match\n" \
              "/helpgame - Lihat semua arahan"
    await update.message.reply_text(message)

async def help_command(update, context):
    message = "📌 Senarai Arahan Tersedia:\n" \
              "/play - Pilih game secara button\n" \
              "/snakegame - Main Snake Game\n" \
              "/memorymatch - Main Memory Match\n" \
              "/helpgame - Lihat semua arahan"
    await update.message.reply_text(message)

async def snakegame(update, context):
    chat = update.effective_chat
    url = get_modified_url(chat, "https://t.me/QuickPlayGameBot/snakegame")
    keyboard = [[InlineKeyboardButton("🐍 Play Snake Game", url=url)]]
    await update.message.reply_text("Klik untuk main Snake Game:", reply_markup=InlineKeyboardMarkup(keyboard))

async def memorymatch(update, context):
    chat = update.effective_chat
    url = get_modified_url(chat, "https://t.me/QuickPlayGameBot/memorymatch")
    keyboard = [[InlineKeyboardButton("🧠 Play Memory Match", url=url)]]
    await update.message.reply_text("Klik untuk main Memory Match:", reply_markup=InlineKeyboardMarkup(keyboard))

async def quicktap(update, context):
    chat = update.effective_chat
    url = get_modified_url(chat, "https://t.me/QuickPlayGameBot/quicktapchallenge")
    keyboard = [[InlineKeyboardButton("⚡ Quick Tap Challenge", url=url)]]
    await update.message.reply_text("Klik untuk main Quick Tap Challenge:", reply_markup=InlineKeyboardMarkup(keyboard))

async def play(update, context):
    chat = update.effective_chat
    snake_game_url = get_modified_url(chat, "https://t.me/QuickPlayGameBot/snakegame")
    memory_match_url = get_modified_url(chat, "https://t.me/QuickPlayGameBot/memorymatch")
    quick_tap_url = get_modified_url(chat, "https://t.me/QuickPlayGameBot/quicktapchallenge")

    keyboard = [
        [InlineKeyboardButton("🐍 Snake Game", url=snake_game_url)],
        [InlineKeyboardButton("🧠 Memory Match", url=memory_match_url)],
        [InlineKeyboardButton("⚡ Quick Tap Challenge", url=quick_tap_url)]
    ]
    await update.message.reply_text("Pilih permainan yang anda mahu mainkan:", reply_markup=InlineKeyboardMarkup(keyboard))

def run_flask_app():
    app.run(host='0.0.0.0', port=5000)

def main():
    try:
        TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
        if not TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN tidak ditetapkan dalam environment variable")

        render_url = os.environ.get("RENDER_EXTERNAL_URL")
        if not render_url:
            raise ValueError("RENDER_EXTERNAL_URL tidak ditetapkan dalam environment variable")

        render_url = render_url.replace("https://", "").replace("http://", "")

        global bot, application
        bot = Bot(TOKEN)
        application = Application.builder().token(TOKEN).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("snakegame", snakegame))
        application.add_handler(CommandHandler("memorymatch", memorymatch))
        application.add_handler(CommandHandler("quicktap", quicktap))
        application.add_handler(CommandHandler("play", play))
        application.add_handler(CommandHandler("helpgame", help_command))

        threading.Thread(target=run_flask_app).start()

        webhook_url = f"https://{render_url}/webhook"
        print(f"Setting webhook to: {webhook_url}")
        application.bot.set_webhook(url=webhook_url)
        application.run_polling()
    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == '__main__':
    main()
