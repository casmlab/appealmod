from pymongo import MongoClient

from core.config import Config as config


class Database:
    def __init__(self):
        client = MongoClient(config.DB_CONNECTION_STRING)
        cluster = client['main-cluster']

        self.responses = cluster['bot-responses']

    def get_responses(self, subreddit):
        cursor = self.responses.find({'subreddit': subreddit})
        output = list(cursor)[0]
        return output


db = Database()
