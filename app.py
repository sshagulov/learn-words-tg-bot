import os
from flask import Flask, request
from bot import Bot
from handlers import handle_update

TOKEN = os.getenv("TOKEN")
URL = os.getenv("NGROK_URL")

app = Flask(__name__)
bot = Bot(TOKEN)


@app.route("/", methods=["GET", "POST"])
def get_updates():
    handle_update(bot, request.json)
    return "OK"


@app.route("/set-webhook", methods=["GET", "POST"])
def set_webhook():
    bot.set_webhook(URL)
    return bot.get_webhook_info()


if __name__ == "__main__":
    app.run(port=5000)
