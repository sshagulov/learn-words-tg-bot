import requests
from data import load_users, load_titles, load_words


class Bot:
    def __init__(self, token):
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{token}/"
        load_users()
        load_titles()
        load_words()

    def get_webhook_info(self):
        response = requests.get(self.api_url + "getWebhookInfo")
        return response.json()

    def set_webhook(self, url):
        response = requests.post(url=self.api_url + "setWebhook", json={"url": url})
        print(response.json())
        return response

    def send_message(self, chat_id, text, reply_markup=None, reply_to_message_id=None):
        response = requests.post(
            self.api_url + "sendMessage",
            {
                "chat_id": chat_id,
                "text": text,
                "reply_markup": reply_markup,
                "reply_to_message_id": reply_to_message_id,
            },
        )
        return response

    def answer_callback_query(self, callback_query_id, text=None, show_alert=False):
        response = requests.post(
            self.api_url + "answerCallbackQuery",
            {
                "callback_query_id": callback_query_id,
                "text": text,
                "show_alert": show_alert,
            },
        )
        return response

    def edit_message_text(self, chat_id, message_id, text, reply_markup=None):
        response = requests.post(
            self.api_url + "editMessageText",
            {
                "chat_id": chat_id,
                "message_id": message_id,
                "text": text,
                "reply_markup": reply_markup,
            },
        )
        return response

    def edit_message_reply_markup(self, chat_id, message_id, keyboard=None):
        response = requests.post(
            self.api_url + "editMessageReplyMarkup",
            {"chat_id": chat_id, "message_id": message_id, "reply_markup": keyboard},
        )
        return response
