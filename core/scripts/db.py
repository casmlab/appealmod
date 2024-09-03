from pymongo import MongoClient

from core.config import Config as config
from core.models.question import Question


class Database:
    def __init__(self):
        cluster = MongoClient(config.DB_CONNECTION_STRING)
        # self.database = cluster['question']
        # self.question = self.database['question']
        # self.answer = self.database['answer']
        self.database = cluster['main-cluster']
        self.responses = self.database['bot-responses']

    def get_responses(self, subreddit):
        cursor = self.responses.find({'subreddit': subreddit})
        output = list(cursor)[0]
        return output

    def import_question(self, object):
        """
        Input: list of Question object
        """
        q_list = []
        for i in object['q']:
            question = {
                "question type": i.question_type,
                "question text": i.question_text,
                "correct answer": i.correct_answer,
                "options": i.options,
            }
            q_list.append(question)
        d = {
            "subreddit": object['subreddit'],
            "q": q_list,
        }
        self.question.insert_many([d])

    def extract_all_question(self):
        """
        Extract all the questions from the database
        """
        return self.question.find()

    def extract_subreddit_questions(self, subreddit):
        """
        Extract questions based on a subreddit
        TODO: parse the value after decides what is needed
        """
        cursor = self.question.find({'subreddit': subreddit})
        return list(cursor)[0]['q']

    def update_subreddit(self, target_subreddit, replace_subreddit):
        """
        Update question on a specific subreddit
        TODO: parse the value after decides what is needed
        TODO: figure out the $set issue
        """
        pass
        # self.question.updateOne(
        #     {"subreddit": target_subreddit},
        #     {$set: {"subreddit": replace_subreddit}}
        # )

    def test_import_question(self, subreddit):
        q1 = Question("question","""A human moderator will assist you soon. In the meantime, I am going to ask some questions that would help in providing a timely response to your message.
First, can you confirm that you want us to reconsider your ban? OR
(a simple yes/no answer would suffice)
(alternative: First can you confirm that you have questions concerning why you were banned?)
""","B",{"A": "Green", "B": "Blue", "G": "Green"})
        q2 = Question("question","""Okay, do you know/understand the reason why you were banned? (the reason is usually part of the first message that was sent to you)
""","C",{"A": "Monday", "B": "Tuesday", "G": "Friday"})

        d = {
            'subreddit': subreddit,
            'q': [q1, q2]
        }
        self.import_question(d)

    def test_extract_all_question(self):
        return self.extract_question()

    def test_extract_subreddit_questions(self, subreddit):
        return self.extract_subreddit_questions(subreddit)
