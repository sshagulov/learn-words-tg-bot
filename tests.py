import random
import uuid
from data import words_dict, curr_tests
from user import User


class Test:
    def __init__(self, theme, num_questions):
        self.id = uuid.uuid4().hex
        self.theme = theme
        self.num_questions = num_questions
        self.current_question = 0
        self.shuffled_word_ids = []

    @staticmethod
    def find_test(test_id):
        return next((test for id, test in curr_tests if id == test_id), None)

    def shuffle_word_ids(self, user_id):
        user: User = User.find_user(str(user_id))
        
        if self.theme not in user.data["learned_words"]:
            user.data["learned_words"][self.theme] = {}
        learned_words = user.data["learned_words"][self.theme]
        
        # получаем массив id вопросов, которых еще не доучили
        # (< num_correct_to_learn) или вообще не учили
        word_ids_to_learn = [
            word["id"]
            for word in words_dict[self.theme]
            if (
                (
                    word["orig"] in learned_words
                    and learned_words[word["orig"]]
                        < user.data["settings"]["num_correct_to_learn"]
                )
                or word["orig"] not in learned_words
            )
        ]

        # добавляем выученные слова в тест, если не хватило вопросов
        if (
            user.data["settings"]["learn_learned_words"] and
            len(word_ids_to_learn) < self.num_questions
        ):
            for _ in range(self.num_questions - len(word_ids_to_learn)):
                while True:
                    random_id = random.randint(0, len(words_dict[self.theme]) - 1)
                    if random_id not in word_ids_to_learn:
                        word_ids_to_learn.append(random_id)
                        break

        if self.num_questions > len(word_ids_to_learn):
            self.num_questions = len(word_ids_to_learn)

        self.shuffled_word_ids = random.sample(word_ids_to_learn, self.num_questions)

    def get_examples(self, num_examples):
        return random.sample(words_dict[self.theme], num_examples)

    def get_word_by_id(self, id):
        return words_dict[self.theme][id]

    def get_current_question(self):
        return self.get_word_by_id(
            self.shuffled_word_ids[self.current_question - 1]
        )
