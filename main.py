from flask import Flask, request, jsonify, render_template_string
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
import requests
import threading
import re
import os

app = Flask(__name__)

# Global variables to store group ID and name
group_id = None
group_name = None

# HTML template as a string
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

def starts_with_symbol_or_emoji(name):
    # Check if the name starts with a symbol or emoji
    return bool(re.match(r'^[^\w\s]', name))

def get_modified_url(chat, base_url):
    if chat.type in ['group', 'supergroup']:
        group_name = chat.title or "Unknown Group"
        if starts_with_symbol_or_emoji(group_name):
            # Use the group's ID in the URL if the group name starts with a symbol or emoji
            url = f"{base_url}?startapp={chat.id}&group_name={group_name}"
        else:
            # Remove spaces from the group name
            modified_group_name = group_name.replace(" ", "")
            # Use the modified group name in the URL
            url = f"{base_url}?startapp={modified_group_name}&{chat.id}"
    elif chat.type == 'private':
        # Use the user's ID directly in the URL for private chats
        url = f"{base_url}?startapp={chat.id}"
    else:
        url = f"{base_url}?startapp=Unknown"
    return url

async def start(update, context):
    chat = update.effective_chat
    user = update.effective_user

    # URL for the web app inline
    WEB_APP_URL = "https://t.me/QuickPlayGameBot/snakegame"

    # Create an inline keyboard with a URL button
    url = get_modified_url(chat, WEB_APP_URL)
    keyboard = [[InlineKeyboardButton("Open Link", url=url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send group info to the backend
    response = requests.post('http://127.0.0.1:5000/update_group_info', json={'group_id': chat.id, 'group_name': chat.title})
    if response.status_code == 200:
        print("Group info sent to server successfully.")
    else:
        print("Failed to send Group info to server.")

    message = "📌 Senarai Arahan Tersedia:\n" \
              "/play - Pilih game secara button\n" \
              "/snakegame - Main Snake Game dalam group\n" \
              "/memorymatch - Main Memory Match dalam group\n" \
              "/help - Lihat semua arahan"
    await update.message.reply_text(message, reply_markup=reply_markup)

async def help_command(update, context):
    message = "📌 Senarai Arahan Tersedia:\n" \
              "/play - Pilih game secara button\n" \
              "/snakegame - Main Snake Game dalam group\n" \
              "/memorymatch - Main Memory Match dalam group\n" \
              "/help - Lihat semua arahan"
    await update.message.reply_text(message)

async def snakegame(update, context):
    chat = update.effective_chat
    WEB_APP_URL = "https://t.me/QuickPlayGameBot/snakegame"
    url = get_modified_url(chat, WEB_APP_URL)
    keyboard = [[InlineKeyboardButton("Play Snake Game", url=url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Klik untuk bermain Snake Game:', reply_markup=reply_markup)

async def memorymatch(update, context):
    chat = update.effective_chat
    WEB_APP_URL = "https://t.me/QuickPlayGameBot/memorymatch"
    url = get_modified_url(chat, WEB_APP_URL)
    keyboard = [[InlineKeyboardButton("Play Memory Match", url=url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Klik untuk bermain Memory Match:', reply_markup=reply_markup)

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
        application.add_handler(CommandHandler("help", help_command))

        # Run Flask in a separate thread
        threading.Thread(target=run_flask_app).start()

        webhook_url = f"https://{render_url}/webhook"
        print(f"Setting webhook to: {webhook_url}")
        application.bot.set_webhook(url=webhook_url)
        application.run_polling()
    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == '__main__':
    main()
