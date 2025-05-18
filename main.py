from flask import Flask, request, jsonify, render_template_string
from telegram.ext import Application, CommandHandler
import requests
import threading

app = Flask(__name__)

# Variabel global untuk menyimpan group ID dan nama grup
group_id = None
group_name = None

# HTML template sebagai string
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
        // Fungsi untuk mengambil group ID dan nama grup dari backend server
        async function fetchGroupInfo() {
            const response = await fetch('/get_group_info');
            const data = await response.json();
            document.getElementById('groupId').textContent = data.group_id;
            document.getElementById('groupName').textContent = data.group_name;
        }

        // Panggil fungsi fetchGroupInfo saat halaman dimuat
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

async def start(update, context):
    chat_id = update.effective_chat.id
    chat_name = update.effective_chat.title if update.effective_chat.title else "Private Chat"
    await update.message.reply_text(f'Group ID: {chat_id}, Group Name: {chat_name}')

    # Kirim group ID dan nama grup ke backend server
    response = requests.post('http://127.0.0.1:5000/update_group_info', json={'group_id': chat_id, 'group_name': chat_name})
    if response.status_code == 200:
        print("Group info sent to server successfully.")
    else:
        print("Failed to send Group info to server.")

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
        application.add_handler(CommandHandler("play", play))
        application.add_handler(CommandHandler("snakegame", snakegame))
        application.add_handler(CommandHandler("memorymatch", memorymatch))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(
            MessageHandler(filters.Regex(f"(?:@)({bot.username})", flags=re.IGNORECASE), mention_reply))

        keep_alive()

        webhook_url = f"https://{render_url}/webhook"
        print(f"Setting webhook to: {webhook_url}")
        application.bot.set_webhook(url=webhook_url)
        application.run_polling()
    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == '__main__':
    main()
