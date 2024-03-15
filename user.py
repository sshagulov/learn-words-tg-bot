import os
import json
from data import users


class User:
    def __init__(self, id, data=None):
        self.id = id
        self.data = {
            "settings": {
                "theme": "emotion",
                "num_questions": 3,
                "num_correct_to_learn": 2,
                "learn_learned_words": False
            },
            "stats": {
                "total_tests": 0,
                "total_correct_answers": 0,
                "total_incorrect_answers": 0,
                "words_learned": 0
            },
            "learned_words": {}
        } if data is None else data
        self.save()

    def save(self):
        with open(f"users/{self.id}.json", "w") as f:
            json.dump(self.data, f, indent=4)

    @staticmethod
    def find_user(user_id):
        return next((user for id, user in users if id == user_id), None)

    @staticmethod
    def load_users():
        if not os.path.exists("users"):
            os.makedirs("users")
        for file in os.listdir("users"):
            if file.endswith(".json"):
                full_path = os.path.join("users", file)
                with open(full_path, "r", encoding="utf-8") as json_f:
                    user_id = os.path.splitext(file)[0]
                    users.add((user_id, User(user_id, data=json.load(json_f))))

