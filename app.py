import os
from flask import Flask, render_template, request
from bot import Bot
from handlers import handle_update

TOKEN = os.getenv("TOKEN")
URL = os.getenv("NGROK_URL")

app = Flask(__name__)
bot = Bot(TOKEN)


@app.route("/", methods=["GET", "POST"])
def get_updates():
    if request.method == 'POST':
        handle_update(bot, request.json)
        return "OK"
    else:
        return render_template(
            "index.html",
            webhook_info=bot.get_webhook_info()
        )


@app.route("/set_webhook", methods=["POST"])
def set_webhook():
    bot.set_webhook(URL)
    return render_template(
        "index.html",
        webhook_info=bot.get_webhook_info()
    )


if __name__ == "__main__":
    app.run(port=5000)
