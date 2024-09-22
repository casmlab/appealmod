from pymongo import MongoClient
from bot.config import Config as config
from bot.models.answer import Answer


class Question:
    def __init__(self,question_type,question_text, correct_answer, options):
        self.question_type = question_type
        self.question_text = question_text
        self.correct_answer = correct_answer
        self.options = options

    def get_question_type(self):
        """
        Return the question type
        """
        return self.q_type

    def get_question_text(self):
        """
        Return the question type
        """
        return self.q_text

    def get_correct_answer(self):
        """
        Return the correct answer
        """
        return self.correct_answer

    def get_options(self):
        """
        Return the options
        """
        return self.options
