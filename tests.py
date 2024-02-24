import random
import uuid
from data import words_dict


class Test:
    def __init__(self, theme, num_questions):
        self.id = uuid.uuid4().hex
        self.theme = theme
        self.num_questions = num_questions
        self.current_question = 0
        self.shuffled_word_ids = random.sample(
            [word["id"] for word in words_dict[self.theme]],
            self.num_questions
        )

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, Test) and self.id == other.id

    def get_examples(self, num_examples):
        return random.sample(words_dict[self.theme], num_examples)

    def get_word_by_id(self, id):
        return words_dict[self.theme][id]

    def get_current_question(self):
        if self.current_question <= self.num_questions:
            return self.get_word_by_id(
                self.shuffled_word_ids[self.current_question - 1]
            )
