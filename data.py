import json
import os

users = {}         # "407752841": { "settings": {}, "stats": {} }
theme_titles = {}  # "emotion": "Эмоции"
words_dict = {}    # "emotion": <содержимое emotion.json>
curr_tests = set() # set("683595fc832e41d1955db61fcc69f39f")
 
default_values = {
    "settings": {
        "theme": "emotion",
        "num_questions": 3,
        "num_correct_to_learn": 2
    },
    "stats": {
        "total_tests": 0,
        "total_correct_answers": 0,
        "total_incorrect_answers": 0,
        "words_learned": 0
    },
    "learned_words": {} # "cooking": { "bake": 0 },
}

def load_users():
    for file in os.listdir("users"):
        if file.endswith(".json"):
            full_path = os.path.join("users", file)
            with open(full_path, "r", encoding="utf-8") as json_file:
                user_id = os.path.splitext(file)[0]
                users[user_id] = json.load(json_file)


def add_user(user_id):
    users[str(user_id)] = default_values
    update_user(user_id)


def update_user(user_id):
    with open(f"users/{user_id}.json", "w") as f:
        json.dump(users[str(user_id)], f, indent=4)


def load_titles():
    for file in os.listdir("themes"):
        full_path = os.path.join("themes", file)
        with open(full_path, "r", encoding="utf-8") as json_file:
            title = json.load(json_file).get("title")
            if title is not None:
                theme_titles[os.path.splitext(file)[0]] = title


def load_words():
    for title in theme_titles:
        with open(f"themes/{title}.json", "r") as f:
            words_dict[title] = json.load(f)["words"]
