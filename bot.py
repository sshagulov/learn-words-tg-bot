import json
import requests
from data import load_titles, load_words
from user import User

class Bot:
    def __init__(self, token):
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{token}/"

        User.load_users()
        load_titles()
        load_words()

    def get_webhook_info(self):
        response = requests.get(self.api_url + "getWebhookInfo")
        return json.dumps(response.json(), indent=4)

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

    def send_photo(self, chat_id, photo, caption=None, reply_markup=None):
        response = requests.post(
            self.api_url + "sendPhoto",
            {
                "chat_id": chat_id,
                "photo": photo,
                "caption": caption,
                "reply_markup": reply_markup,
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

    def edit_message_media(self, chat_id, message_id, media, reply_markup=None):
        response = requests.post(
            self.api_url + "editMessageMedia",
            {
                "chat_id": chat_id,
                "message_id": message_id,
                "media": media,
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
