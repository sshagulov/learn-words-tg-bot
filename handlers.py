import random
import re
from bot import Bot
from tests import Test
from data import curr_tests, users, add_user, update_user
from keyboard import Button, Keyboard, back_keyboard, home_keyboard, settings_keyboard, answer_keyboard


def handle_update(bot: Bot, update):

    handlers = {
        "home": handle_home,
        "test": handle_test_start,
        "answer": handle_answer,
        "settings": handle_settings,
        "stats": handle_stats,
    }

    if "message" in update and "text" in update["message"]:
        message = update["message"]["text"]

        if message == "/start":
            chat_id = update["message"]["chat"]["id"]
            if str(chat_id) not in users:
                add_user(chat_id)
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

    settings = users[str(chat_id)]["settings"]
    test = Test(settings["theme"], settings["num_questions"])
    curr_tests.add(test)

    handle_next_question(bot, update, test.id)


def handle_test_cancel(bot: Bot, update, test_id):
    chat_id = update["message"]["chat"]["id"]
    message_id = update["message"]["message_id"]

    test = next((obj for obj in curr_tests if obj.id == test_id), None)
    if test is None: return

    users[str(chat_id)]["stats"]["total_tests"] += 1
    update_user(chat_id)
    curr_tests.remove(test)

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

    test: Test = next((obj for obj in curr_tests if obj.id == test_id), None)
    if test is None: return

    test.current_question += 1
    question = test.get_current_question()
    examples = test.get_examples(4)

    if not any(question == example for example in examples):
        index_to_replace = random.randint(0, len(examples) - 1)
        examples[index_to_replace] = question

    keyboard = Keyboard([
        [Button(
            example['translation'],
            f"ans_{test.id}_{example['id']}_{question['id']}"
        )] for example in examples
    ])

    bot.answer_callback_query(update["id"])
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=f"Вопрос {test.current_question}/{test.num_questions}: {question['word']}",
        reply_markup=keyboard.to_json(),
    )


def handle_answer(bot: Bot, update, answer):
    chat_id = update["message"]["chat"]["id"]
    message_id = update["message"]["message_id"]
    
    # 683595fc832e41d1955db61fcc69f39f_11_11
    test_id, question_id, answer_id = answer.split('_')
    test: Test = next((obj for obj in curr_tests if obj.id == test_id), None)
    if test is None: return

    if test.theme not in users[str(chat_id)]["learned_words"]:
        users[str(chat_id)]["learned_words"][test.theme] = {}
    
    stats = users[str(chat_id)]["stats"]
    learned_words = users[str(chat_id)]["learned_words"][test.theme]
    
    correct = answer_id == question_id
    if correct:
        stats["total_correct_answers"] += 1
        
        word = test.get_word_by_id(int(question_id))
        if word["word"] not in learned_words:
            learned_words[word["word"]] = 0
        
        learned_words[word["word"]] += 1
    else:
        stats["total_incorrect_answers"] += 1
    
    question = test.get_word_by_id(int(question_id))
    qa = f"\n{question['word']} - {question['translation']}\n"

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
    
    stats = users[str(chat_id)]["stats"]
    stats_str = """📊 Статистика\n
Всего тестов: {total_tests}
Правильных ответов: {total_correct_answers}
Неправильных ответов: {total_incorrect_answers}
Слов изучено: {words_learned}
""".format(**stats)

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
                [Button("Готовка", "set_theme_cooking")],
                [Button("Эмоции", "set_theme_emotion")],
                [Button("Назад", "settings"), Button("На главную", "home")],
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

    if setting != "theme":
        value = int(value)
    
    settings = users[str(chat_id)]["settings"]
    settings[setting] = value
    update_user(chat_id)

    bot.answer_callback_query(update["id"])
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text="⚙️ Настройки",
        reply_markup=settings_keyboard(chat_id),
    )
