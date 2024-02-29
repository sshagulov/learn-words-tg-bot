import random
import re
from bot import Bot
from tests import Test
from user import User
from data import curr_tests, users, theme_titles
from keyboard import (
    Button,
    Keyboard,
    back_keyboard,
    home_keyboard,
    settings_keyboard,
    answer_keyboard,
    relearn_keyboard,
)

def handle_update(bot: Bot, update):

    handlers = {
        "home": handle_home,
        "relearn": handle_relearn,
        "test": handle_test_start,
        "answer": handle_answer,
        "settings": handle_settings,
        "stats": handle_stats,
    }

    if "message" in update and "text" in update["message"]:
        message = update["message"]["text"]

        if message == "/start":
            handle_home(bot, update)

    elif "callback_query" in update:

        data = update["callback_query"]["data"]

        # change_num_questions
        match = re.match(r"^change_(.*)$", data)
        if match:
            handle_set(bot, update["callback_query"], match.group(1))

        # set_num_questions_20
        match = re.match(r"^set_(.*)$", data)
        if match:
            remaining = match.group(1)
            last_underscore = remaining.rfind("_")
            
            setting = remaining[:last_underscore]
            value = remaining[last_underscore + 1 :]
            
            handle_set_value(bot, update["callback_query"], setting, value)

        # next_683595fc832e41d1955db61fcc69f39f
        match = re.match(r"^next_(.*)$", data)
        if match:
            handle_next_question(bot, update["callback_query"], match.group(1))

        # ans_683595fc832e41d1955db61fcc69f39f_11_11
        match = re.match(r"^ans_(.*)$", data)
        if match:
            handle_answer(bot, update["callback_query"], match.group(1))

        # cancel_683595fc832e41d1955db61fcc69f39f
        match = re.match(r"^cancel_(.*)$", data)
        if match:
            handle_test_cancel(bot, update["callback_query"], match.group(1))

        if data in handlers:
            handlers[data](bot, update["callback_query"])


def handle_home(bot: Bot, update):
    chat_id = update["message"]["chat"]["id"]
    message_id = update["message"]["message_id"]

    user = User.find_user(str(chat_id))
    if not user:
        users.add((chat_id, User(chat_id)))

    if "id" in update:
        bot.answer_callback_query(update["id"])
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="Выберите действие: ",
            reply_markup=home_keyboard,
        )
    else:
        bot.send_message(chat_id, "Выберите действие: ", home_keyboard)


def handle_test_start(bot: Bot, update):
    chat_id = update["message"]["chat"]["id"]
    message_id = update["message"]["message_id"]

    user: User = User.find_user(str(chat_id))
    settings = user.data["settings"]

    test = Test(settings["theme"], settings["num_questions"])
    test.shuffle_word_ids(chat_id)

    if len(test.shuffled_word_ids) < 1:

        bot.answer_callback_query(update["id"])
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="Вы выучили все слова из этой темы!",
            reply_markup=relearn_keyboard,
        )
        return

    curr_tests.add((test.id, test))
    handle_next_question(bot, update, test.id)


def handle_relearn(bot: Bot, update):
    chat_id = update["message"]["chat"]["id"]
    message_id = update["message"]["message_id"]

    user: User = User.find_user(str(chat_id))
    user.data["learned_words"][user.data["settings"]["theme"]] = {}
    user.save()

    bot.answer_callback_query(update["id"])
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text="Выберите действие: ",
        reply_markup=home_keyboard,
    )


def handle_test_cancel(bot: Bot, update, test_id):
    chat_id = update["message"]["chat"]["id"]
    message_id = update["message"]["message_id"]

    user: User = User.find_user(str(chat_id))
    user.data["stats"]["total_tests"] += 1
    user.save()

    test: Test = Test.find_test(test_id)
    if test:
        curr_tests.discard((test.id, None))

    bot.answer_callback_query(update["id"])
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text="Выберите действие: ",
        reply_markup=home_keyboard,
    )


def handle_next_question(bot: Bot, update, test_id):
    chat_id = update["message"]["chat"]["id"]
    message_id = update["message"]["message_id"]

    test: Test = Test.find_test(test_id)
    test.current_question += 1
    question = test.get_current_question()
    examples = test.get_examples(4)

    if not any(question == example for example in examples):
        index_to_replace = random.randint(0, len(examples) - 1)
        examples[index_to_replace] = question

    keyboard = Keyboard([
        [Button(
            example['translation'],
            f"ans_{test.id}_{question['id']}_{example['id']}"
        )] for example in examples
    ])

    bot.answer_callback_query(update["id"])
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=f"Вопрос {test.current_question}/{test.num_questions}: {question['orig']}",
        reply_markup=keyboard.to_json(),
    )


def handle_answer(bot: Bot, update, answer):
    chat_id = update["message"]["chat"]["id"]
    message_id = update["message"]["message_id"]

    # 683595fc832e41d1955db61fcc69f39f_11_11
    test_id, question_id, answer_id = answer.split('_')

    test: Test = Test.find_test(test_id)
    user: User = User.find_user(str(chat_id))

    if test.theme not in user.data["learned_words"]:
        user.data["learned_words"][test.theme] = {}

    stats = user.data["stats"]
    learned_words = user.data["learned_words"][test.theme]
    word = test.get_word_by_id(int(question_id))

    correct = answer_id == question_id
    if correct:
        stats["total_correct_answers"] += 1
        
        if word["orig"] not in learned_words:
            learned_words[word["orig"]] = 0

        learned_words[word["orig"]] += 1
    else:
        stats["total_incorrect_answers"] += 1
        
        if word["orig"] in learned_words:
            learned_words[word["orig"]] = 0
    
    question = test.get_word_by_id(int(question_id))
    qa = f"\n{question['orig']} - {question['translation']}\n"

    bot.answer_callback_query(update["id"])
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text="Правильно!" + qa if correct else "Неправильно!" + qa,
        reply_markup=answer_keyboard(
            test_id,
            is_last=test.current_question == test.num_questions
        ),
    )


def handle_stats(bot: Bot, update):
    chat_id = update["message"]["chat"]["id"]
    message_id = update["message"]["message_id"]
    
    user = User.find_user(str(chat_id))
    stats = user.data["stats"]
    
    words_learned = ""
    for theme, words in user.data["learned_words"].items():
        learned_num = sum(value for value in words.values() if value >= 2)
        words_learned += f"\n\u2022 {theme_titles[theme]}: {learned_num}"
    
    stats_str = """📊 Статистика\n
Всего тестов: {total_tests}
Правильных ответов: {total_correct_answers}
Неправильных ответов: {total_incorrect_answers}
Слов изучено (по темам): {words_learned}
""".format(
        total_tests=stats["total_tests"],
        total_correct_answers=stats["total_tests"],
        total_incorrect_answers=stats["total_incorrect_answers"],
        words_learned=words_learned
    )

    bot.answer_callback_query(update["id"])
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=stats_str,
        reply_markup=back_keyboard,
    )


def handle_settings(bot: Bot, update):
    chat_id = update["message"]["chat"]["id"]
    message_id = update["message"]["message_id"]
    
    bot.answer_callback_query(update["id"])
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text="⚙️ Настройки:",
        reply_markup=settings_keyboard(chat_id),
    )


def handle_set(bot: Bot, update, setting: str):
    chat_id = update["message"]["chat"]["id"]
    message_id = update["message"]["message_id"]

    match setting:
        case "theme":
            keyboard = Keyboard([
                [Button(title, f"set_theme_{theme}")]
                for theme, title in theme_titles.items()
            ] + [
                [Button("Назад", "settings"), Button("На главную", "home")]
            ])
            setting_name = "тему"

        case "num_questions":
            keyboard = Keyboard([
                [
                    Button("1", "set_num_questions_1"),
                    Button("3", "set_num_questions_3"),
                    Button("6", "set_num_questions_6")
                ],
                [
                    Button("10", "set_num_questions_10"),
                    Button("15", "set_num_questions_15"),
                    Button("20", "set_num_questions_20")
                ],
                [Button("Назад", "settings"), Button("На главную", "home")],
            ])
            setting_name = "количество вопросов в тесте"

        case "num_correct_to_learn":
            keyboard = Keyboard([
                [
                    Button("1", "set_num_correct_to_learn_1"),
                    Button("2", "set_num_correct_to_learn_2"),
                    Button("3", "set_num_correct_to_learn_3")
                ],
                [
                    Button("4", "set_num_correct_to_learn_4"),
                    Button("5", "set_num_correct_to_learn_5"),
                    Button("6", "set_num_correct_to_learn_6")
                ],
                [Button("Назад", "settings"), Button("На главную", "home")],
            ])
            setting_name = "количество повторов слова для полного изучения"

        case _:
            return
        
    bot.answer_callback_query(update["id"])
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text="Выбери " + setting_name,
        reply_markup=keyboard.to_json(),
    )            


def handle_set_value(bot: Bot, update, setting: str, value: str):
    chat_id = update["message"]["chat"]["id"]
    message_id = update["message"]["message_id"]

    if setting in ["num_questions", "num_correct_to_learn"]:
        value = int(value)

    if setting == "learn_learned_words":
        value = True if value == "True" else False

    user: User = User.find_user(str(chat_id))
    user.data["settings"][setting] = value
    user.save()

    bot.answer_callback_query(update["id"])
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text="⚙️ Настройки",
        reply_markup=settings_keyboard(chat_id),
    )
