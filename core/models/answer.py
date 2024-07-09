from pymongo import MongoClient
from core.config import Config as config


class Answer:
    def __init__(self, correct_answer, options):
        self.answer = correct_answer
        self.options = options

    def get_answer(self):
        """
        Return the answer
        """
        return self.answer

    def get_options(self):
        """
        Return the options of the answer
        """
        return self.options
