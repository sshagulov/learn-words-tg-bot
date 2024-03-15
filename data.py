import json
import os

users = set()      # set((User.id, User), ...)
words_dict = {}    # "emotion": <поле "words" в emotion.json>
theme_titles = {}  # "emotion": "Эмоции"
curr_tests = set() # set((Test.id, Test), ...)

def load_titles():
    for file in os.listdir("themes"):
        full_path = os.path.join("themes", file)
        with open(full_path, "r", encoding="utf-8") as json_file:
            title = json.load(json_file).get("title")
            if title is not None:
                theme_titles[os.path.splitext(file)[0]] = title


def load_words():
    for title in theme_titles:
        with open(f"themes/{title}.json", "r", encoding="utf-8") as f:
            words_dict[title] = json.load(f)["words"]
