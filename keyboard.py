import json
from data import theme_titles
from user import User


class Button:
    def __init__(self, text, callback_data):
        self.text = text
        self.callback_data = callback_data

    def to_dict(self):
        return {"text": self.text, "callback_data": self.callback_data}

    def to_json(self):
        return json.dumps(self.to_dict())


class Keyboard:
    def __init__(self, rows=None):
        self.rows = rows if rows else []

    def add_row(self, row):
        self.rows.append(row)

    def to_json(self):
        button_dicts = [[button.to_dict() for button in row] for row in self.rows]
        return json.dumps({"inline_keyboard": button_dicts})


def settings_keyboard(chat_id):
    user = User.find_user(str(chat_id))
    settings = user.data["settings"]
    
    theme = theme_titles[settings["theme"]]
    num_questions = str(settings["num_questions"])
    num_correct_to_learn = str(settings["num_correct_to_learn"])
    learn_learned_words = settings["learn_learned_words"]

    return Keyboard([
        [Button(
            "Тема: " + theme,
            "change_theme"
        )],
        [Button(
            "Количество вопросов: " + num_questions,
            "change_num_questions",
        )],
        [Button(
            "Количество повторов слова для полного изучения: "
            + num_correct_to_learn,
            "change_num_correct_to_learn",
        )],
        [Button(
            "Включать выученные слова в тест: "
            + ("Да" if learn_learned_words else "Нет"),
            f"set_learn_learned_words_{not learn_learned_words}"
        )],
        [Button("Назад", "home")],
    ]).to_json()


def answer_keyboard(test_id, is_last=False):
    if is_last:
        return Keyboard([[
            Button("Закончить тест", f"cancel_{test_id}"),
        ]]).to_json()
    else:
        return Keyboard([[
            Button("Дальше", f"next_{test_id}"),
            Button("Закончить тест", f"cancel_{test_id}"),
        ]]).to_json()


home_keyboard = Keyboard([
    [Button("🏁 Начать тест", "test")],
    [Button("📊 Статистика", "stats"), Button("⚙️ Настройки", "settings")],
]).to_json()


back_keyboard = Keyboard([[Button("Назад", "home")]]).to_json()


relearn_keyboard = Keyboard([
    [Button("Начать заново", "relearn")],
    [Button("Сменить тему", "change_theme")],
    [Button("Назад", "home")],
]).to_json()